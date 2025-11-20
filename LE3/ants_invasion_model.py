from __future__ import annotations
from typing import Optional

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


# ==========================================================
# Agenten
# ==========================================================

class ResourcePatch(Agent):
    """
    Ressourcen-Patch (Futter) für beide Ameisentypen.

    amount     = aktuelle Nahrungsmenge
    max_amount = maximale Kapazität
    regen_rate = Regeneration pro Schritt (absolute Menge)
    """

    def __init__(self, model: Model, amount: float, max_amount: float, regen_rate: float):
        super().__init__(model)
        self.amount = float(amount)
        self.max_amount = float(max_amount)
        self.regen_rate = float(regen_rate)

    def step(self):
        if self.regen_rate <= 0.0:
            return
        self.amount = min(self.max_amount, self.amount + self.regen_rate)


class NativeAnt(Agent):
    """
    Einheimische Ameise.

    - frisst Ressourcen
    - Fortpflanzung hängt positiv von habitat_quality ab
    - kann von invasiven Ameisen getötet/unterdrückt werden
    """

    def __init__(
        self,
        model: Model,
        energy: float,
        metabolism: float,
        bite_size: float,
        base_reproduce_prob: float,
        reproduce_threshold: float,
    ):
        super().__init__(model)
        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        self.base_reproduce_prob = float(base_reproduce_prob)
        self.reproduce_threshold = float(reproduce_threshold)

    # ---------- Verhalten ----------

    def move(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )
        new_pos = self.random.choice(neighbors)
        self.model.grid.move_agent(self, new_pos)

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        patches = [a for a in cellmates if isinstance(a, ResourcePatch)]
        if not patches:
            return
        patch = patches[0]
        take = min(self.bite_size, patch.amount)
        if take > 0:
            patch.amount -= take
            self.energy += take

    def maybe_reproduce(self):
        # Reproduktionswahrscheinlichkeit skaliert mit habitat_quality (0..1)
        h = max(0.0, min(1.0, self.model.habitat_quality))
        p = self.base_reproduce_prob * h
        if self.energy >= self.reproduce_threshold and self.random.random() < p:
            child_energy = self.energy * 0.5
            self.energy *= 0.5

            child = NativeAnt(
                model=self.model,
                energy=child_energy,
                metabolism=self.metabolism,
                bite_size=self.bite_size,
                base_reproduce_prob=self.base_reproduce_prob,
                reproduce_threshold=self.reproduce_threshold,
            )
            self.model.grid.place_agent(child, self.pos)

    def die(self):
        self.model.grid.remove_agent(self)
        self.remove()

    def step(self):
        # Grundumsatz
        self.energy -= self.metabolism
        if self.energy <= 0:
            self.die()
            return

        self.move()
        self.eat()
        self.maybe_reproduce()


class InvasiveAnt(Agent):
    """
    Invasive Ameise.

    - frisst Ressourcen
    - Fortpflanzung hängt positiv von der Ressourcensituation ab
    - tötet einheimische Ameisen mit Wahrscheinlichkeit attack_prob
    """

    def __init__(
        self,
        model: Model,
        energy: float,
        metabolism: float,
        bite_size: float,
        base_reproduce_prob: float,
        reproduce_threshold: float,
        attack_prob: float,
    ):
        super().__init__(model)
        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        self.base_reproduce_prob = float(base_reproduce_prob)
        self.reproduce_threshold = float(reproduce_threshold)
        self.attack_prob = float(attack_prob)

    def move(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )
        new_pos = self.random.choice(neighbors)
        self.model.grid.move_agent(self, new_pos)

    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        patches = [a for a in cellmates if isinstance(a, ResourcePatch)]
        if not patches:
            return
        patch = patches[0]
        take = min(self.bite_size, patch.amount)
        if take > 0:
            patch.amount -= take
            self.energy += take

    def attack_natives(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        natives = [a for a in cellmates if isinstance(a, NativeAnt)]
        for ant in natives:
            if self.random.random() < self.attack_prob:
                ant.die()

    def maybe_reproduce(self):
        # Reproduktion positiv beeinflusst durch Ressourcenniveau
        res_frac = self.model.resource_fraction()  # 0..1
        p = self.base_reproduce_prob * res_frac
        if self.energy >= self.reproduce_threshold and self.random.random() < p:
            child_energy = self.energy * 0.5
            self.energy *= 0.5
            child = InvasiveAnt(
                model=self.model,
                energy=child_energy,
                metabolism=self.metabolism,
                bite_size=self.bite_size,
                base_reproduce_prob=self.base_reproduce_prob,
                reproduce_threshold=self.reproduce_threshold,
                attack_prob=self.attack_prob,
            )
            self.model.grid.place_agent(child, self.pos)

    def die(self):
        self.model.grid.remove_agent(self)
        self.remove()

    def step(self):
        self.energy -= self.metabolism
        if self.energy <= 0:
            self.die()
            return

        self.move()
        self.eat()
        self.attack_natives()
        self.maybe_reproduce()


# ==========================================================
# Model
# ==========================================================

class AntInvasionModel(Model):
    """
    Agentenbasiertes Modell passend zu deinem Kausaldiagramm.

    - NativeAnt  ~ "Ameisen"
    - InvasiveAnt ~ "Invasive Arten"
    - ResourcePatch ~ "Ressourcen für invasive Art"
    - habitat_quality (0..1) ~ "Habitatsqualität"
    - warming (°C) ~ "Erderwärmung exogen"
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        initial_native: int = 40,
        initial_invasive: int = 5,
        resource_density: float = 0.7,
        patch_max: float = 10.0,
        patch_initial_share: float = 0.7,
        patch_regen: float = 0.05,
        native_energy: float = 5.0,
        invasive_energy: float = 5.0,
        metabolism_native: float = 0.2,
        metabolism_invasive: float = 0.25,
        bite_native: float = 0.8,
        bite_invasive: float = 1.0,
        native_repro_base: float = 0.15,
        invasive_repro_base: float = 0.18,
        repro_threshold_native: float = 8.0,
        repro_threshold_invasive: float = 8.0,
        attack_prob: float = 0.4,
        # Umwelt / Stocks
        habitat_quality_start: float = 1.0,     # 1.0 = 100 %
        warming_start: float = 0.0,            # ΔT in °C
        warming_rate: float = 0.02,            # Zunahme pro Schritt
        climate_habitat_loss: float = 0.005,   # Habitatverlust nur durch Klima / Schritt
        invasive_habitat_impact: float = 0.001,  # zusätzl. Verlust pro invasiver Ameise / Schritt
        seed: Optional[int] = 42,
    ):
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)

        # Globale Stocks
        self.habitat_quality = habitat_quality_start
        # (0..1-Skala)
        self.warming = warming_start
        self.warming_rate = warming_rate
        self.climate_habitat_loss = climate_habitat_loss
        self.invasive_habitat_impact = invasive_habitat_impact

        # Ressourcen-Patches
        self.initial_total_resources = 0.0
        for x in range(width):
            for y in range(height):
                has_res = self.random.random() < resource_density
                amount = patch_max * patch_initial_share if has_res else 0.0
                patch = ResourcePatch(
                    model=self,
                    amount=amount,
                    max_amount=patch_max,
                    regen_rate=patch_regen,
                )
                self.grid.place_agent(patch, (x, y))
                self.initial_total_resources += amount

        # Einheimische Ameisen
        for _ in range(initial_native):
            ant = NativeAnt(
                model=self,
                energy=native_energy,
                metabolism=metabolism_native,
                bite_size=bite_native,
                base_reproduce_prob=native_repro_base,
                reproduce_threshold=repro_threshold_native,
            )
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(ant, (x, y))

        # Invasive Ameisen
        for _ in range(initial_invasive):
            ant = InvasiveAnt(
                model=self,
                energy=invasive_energy,
                metabolism=metabolism_invasive,
                bite_size=bite_invasive,
                base_reproduce_prob=invasive_repro_base,
                reproduce_threshold=repro_threshold_invasive,
                attack_prob=attack_prob,
            )
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(ant, (x, y))

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "NativeAnts": lambda m: m.count_native(),
                "InvasiveAnts": lambda m: m.count_invasive(),
                "TotalResources": lambda m: m.total_resources(),
                "HabitatQuality": lambda m: float(m.habitat_quality),
                "Warming": lambda m: float(m.warming),
            }
        )

    # ----- Auswertungsfunktionen ----------------------------------

    def count_native(self) -> int:
        if NativeAnt not in self.agents_by_type:
            return 0
        return len(self.agents_by_type[NativeAnt])

    def count_invasive(self) -> int:
        if InvasiveAnt not in self.agents_by_type:
            return 0
        return len(self.agents_by_type[InvasiveAnt])

    def total_resources(self) -> float:
        if ResourcePatch not in self.agents_by_type:
            return 0.0
        return sum(p.amount for p in self.agents_by_type[ResourcePatch])

    def resource_fraction(self) -> float:
        if self.initial_total_resources <= 0:
            return 0.0
        return max(0.0, min(1.0, self.total_resources() / self.initial_total_resources))

    # ----- Umweltupdate -------------------------------------------

    def update_environment(self):
        # Erderwärmung exogen ↑ (in °C)
        self.warming += self.warming_rate

        # Klimabedingter Habitatverlust + zusätzlicher Verlust durch invasive Ameisen
        inv = self.count_invasive()
        delta = self.climate_habitat_loss + inv * self.invasive_habitat_impact

        # additive Abnahme, begrenzt auf [0, 1]
        self.habitat_quality = max(0.0, min(1.0, self.habitat_quality - delta))

    # ----- Simulationsschritt -------------------------------------

    def step(self):
        # 1) Einheimische Ameisen
        if NativeAnt in self.agents_by_type:
            self.agents_by_type[NativeAnt].shuffle_do("step")

        # 2) Invasive Ameisen
        if InvasiveAnt in self.agents_by_type:
            self.agents_by_type[InvasiveAnt].shuffle_do("step")

        # 3) Ressourcen regenerieren
        if ResourcePatch in self.agents_by_type:
            self.agents_by_type[ResourcePatch].do("step")

        # 4) Globale Stocks (Habitat, Erderwärmung) updaten
        self.update_environment()

        # 5) Daten sammeln
        self.datacollector.collect(self)


# ==========================================================
# Einfacher Lauf über die Konsole (ohne GUI)
# ==========================================================

if __name__ == "__main__":
    model = AntInvasionModel()

    n_steps = 50
    for t in range(n_steps):
        model.step()
        print(
            f"Step {t:3d} | "
            f"Native = {model.count_native():3d} | "
            f"Invasive = {model.count_invasive():3d} | "
            f"Res = {model.total_resources():6.1f} | "
            f"Habitat = {model.habitat_quality:5.3f} | "
            f"Warming = {model.warming:5.3f}"
        )

    df = model.datacollector.get_model_vars_dataframe()
    print("\nLetzte 5 Zeilen der gesammelten Daten:")
    print(df.tail())
