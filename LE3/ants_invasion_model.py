from __future__ import annotations
from typing import Optional

import random

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


class NativeAntHill(Agent):
    """
    Ameisenhügel für die einheimischen Ameisen.

    - speichert Nahrung (stored_food)
    - produziert neue NativeAnts, wenn genug Nahrung vorhanden ist
      (Königin-Logik: Fortpflanzung passiert hier, nicht bei den Arbeiterinnen)
    """

    def __init__(
        self,
        model: Model,
        stored_food_native: float = 0.0,
        max_new_ants_per_step: int = 1,
    ):
        super().__init__(model)
        self.stored_food_native = float(stored_food_native)
        self.max_new_ants_per_step = int(max_new_ants_per_step)

    def receive_food(self, amount: float) -> float:
        """
        Ameisen können Nahrung in den Hügel einlagern.
        Gibt die tatsächlich akzeptierte Menge zurück (falls Kapazität begrenzt).
        """
        if amount <= 0.0:
            return 0.0

        self.stored_food_native += amount
        return amount

    def step(self):
        """
        Königin-Logik: Wenn genug Nahrung gespeichert ist, erzeugt der Hügel neue Ameisen.
        Die Reproduktion hängt außerdem positiv von habitat_quality ab.
        """

        # 0..1 – schlechte Habitatqualität dämpft Reproduktion
        h = max(0.0, min(1.0, self.model.habitat_quality))
        if h <= 0.0:
            return

        for _ in range(self.max_new_ants_per_step):
            # pro Schritt max_new_ants_per_step neue Ameisen,
            # solange genug Nahrung vorhanden ist
            if self.stored_food_native < 1.0:
                break

            # neue Arbeiterin erzeugen (Arbeiterinnen reproduzieren nicht selbst)
            ant = NativeAnt(
                model=self.model,
                energy=self.model.native_energy,
                metabolism=self.model.metabolism_native,
                bite_size=self.model.bite_native,
            )
            self.model.grid.place_agent(ant, self.pos)

            self.stored_food_native -= 1.0  # einfache "Kosten" pro neuer Ameise


class NativeAnt(Agent):
    """
    Einheimische Ameise.

    - frisst Ressourcen
    - wird über den Ameisenhügel (Königin) vermehrt
    - kann von invasiven Ameisen getötet/unterdrückt werden
    """

    def __init__(
        self,
        model: Model,
        energy: float,
        metabolism: float,
        bite_size: float,
    ):
        super().__init__(model)
        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        # bleiben als Felder vorhanden, werden aber nicht benutzt (Arbeiterinnen reproduzieren nicht)
        
        # Energiepuffer, damit die Ameise sich nicht komplett "leer" macht
        self.min_energy = 6
        self.return_threshold = 6.0
        self.min_food_to_move = 1.0
        self.mode = "search"  # "search" | "return"
        self.max_energy = 208
        self.max_foraging_dist = 15

    # ---------- Verhalten ----------

    def move(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        # --------------------------------------------------
        # 1) Suchmodus: probabilistische Umkehr bei Energiemangel
        # --------------------------------------------------
        if self.mode == "search":
            energy_frac = self.energy / self.max_energy  # 0..1

            if energy_frac > 0.5:
                # steigt von 0 bis 0.5 zwischen 50% und 100% Energie
                p_return = (energy_frac - 0.5) / 0.5 * 0.5
                if self.random.random() < p_return:
                    self.mode = "return"
        
        if self.mode == "search":
            # je leerer, desto höher die Rückkehrwahrscheinlichkeit
            energy_frac = self.energy / self.max_energy  

            # über 50 % Energie: Rückkehr wird wahrscheinlicher
            if energy_frac > 0.5:
                p_return = min(0.5, (0.5 - energy_frac))
                if self.random.random() < p_return:
                    self.mode = "return"

        # --------------------------------------------------
        # 2) Rückkehrmodus: zielgerichtet zum Nest
        # --------------------------------------------------
        if self.mode == "return":
            target = self.nearest_hill_pos()
            if target is not None:

                def dist2(a, b):
                    dx = a[0] - b[0]
                    dy = a[1] - b[1]
                    return dx * dx + dy * dy

                best = min(neighbors, key=lambda n: dist2(n, target))
                self.model.grid.move_agent(self, best)
                return

        # --------------------------------------------------
        # 3) Suchmodus: lokale Exploration
        # --------------------------------------------------
        hill = self.nearest_hill_pos()
        if hill is not None and self.random.random() < 0.4:
            hx, hy = hill

            farther = [
                n for n in neighbors
                if abs(n[0] - hx) + abs(n[1] - hy) >
                abs(self.pos[0] - hx) + abs(self.pos[1] - hy)
            ]

            if farther:
                self.model.grid.move_agent(self, self.random.choice(farther))
                return

        # --------------------------------------------------
        # 4) Fallback: reiner Random Walk
        # --------------------------------------------------
        self.model.grid.move_agent(self, self.random.choice(neighbors))



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
        if self.energy >= self.max_energy:
            self.mode = "return"


    def deposit_food(self):
        """
        Wenn die Ameise sich auf einem Feld mit einem NativeAntHill befindet,
        lagert sie einen Teil ihrer Energie als Nahrung in den Hügel ein.
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        hills = [a for a in cellmates if isinstance(a, NativeAntHill)]
        if not hills:
            return

        hill = hills[0]

        # Nur Energie oberhalb eines Mindestpuffers kann eingelagert werden
        available = max(0.0, self.energy - self.min_energy)
        if available <= 0.0:
            return
        accepted = hill.receive_food(available)
        if accepted > 0:
            self.energy -= accepted
            self.mode = "search"


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
        # keine Selbst-Reproduktion mehr
        self.deposit_food()
    
    def nearest_hill_pos(self):
        """
        Finde die Position des nächstgelegenen NativeAntHill (falls vorhanden).
        Berücksichtigt torus-Grid.
        """
        from ants_invasion_model import NativeAntHill  # falls oben nicht importiert

        hills = self.model.agents_by_type.get(NativeAntHill, [])
        if not hills:
            return None

        x, y = self.pos
        width, height = self.model.width, self.model.height

        best_pos = None
        best_d2 = None

        for hill in hills:
            hx, hy = hill.pos
            dx = min(abs(hx - x), width - abs(hx - x))
            dy = min(abs(hy - y), height - abs(hy - y))
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                best_pos = (hx, hy)

        return best_pos

class InvasiveAntHill(Agent):
    """
    Ameisenhügel für die invasiven Ameisen.

    - speichert Nahrung (stored_food)
    - produziert neue InvasiveAnts, wenn genug Nahrung vorhanden ist
      (Königin-Logik: Fortpflanzung passiert hier, nicht bei den Arbeiterinnen)
    """

    def __init__(
        self,
        model: Model,
        stored_food_invasive: float = 0.0,
        max_new_ants_per_step: int = 6,
    ):
        super().__init__(model)
        self.stored_food_invasive = float(stored_food_invasive)
        self.max_new_ants_per_step = int(max_new_ants_per_step)

    def receive_food(self, amount: float) -> float:
        """
        Ameisen können Nahrung in den Hügel einlagern.
        Gibt die tatsächlich akzeptierte Menge zurück (falls Kapazität begrenzt).
        """
        if amount <= 0.0:
            return 0.0

        self.stored_food_invasive += amount
        return amount

    def step(self):
        """
        Königin-Logik: Wenn genug Nahrung gespeichert ist, erzeugt der Hügel neue Ameisen.
        Die Reproduktion hängt außerdem positiv von habitat_quality ab.
        """


        for _ in range(self.max_new_ants_per_step):
            # pro Schritt max_new_ants_per_step neue Ameisen,
            # solange genug Nahrung vorhanden ist
            if self.stored_food_invasive < 1.0:
                break

            # neue Arbeiterin erzeugen (Arbeiterinnen reproduzieren nicht selbst)
            ant = InvasiveAnt(
                model=self.model,
                energy=self.model.invasive_energy,
                metabolism=self.model.metabolism_invasive,
                bite_size=self.model.bite_invasive,
                attack_prob=self.model.attack_prob,
            )
            self.model.grid.place_agent(ant, self.pos)

            self.stored_food_invasive -= 1.0  # einfache "Kosten" pro neuer Ameise

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
        attack_prob: float,
    ):
        super().__init__(model)
        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        self.attack_prob = float(attack_prob)
        self.min_energy = 1.0
        self.return_threshold = 6.0
        self.min_food_to_move = 1.0
        self.mode = "search"
        self.max_energy = 14.0   # invasiv = etwas höhere Kapazität


    def move(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

        # --------------------------------------------------
        # 1) Suchmodus: energie-abhängige Rückkehr (später als bei NativeAnt)
        # --------------------------------------------------
        if self.mode == "search":
            energy_frac = self.energy / self.max_energy  # 0..1

            if energy_frac > 0.4:
                # steigt von 0 bis 0.3 zwischen 40% und 100% Energie
                p_return = (energy_frac - 0.4) / 0.6 * 0.3
                if self.random.random() < p_return:
                    self.mode = "return"


        # --------------------------------------------------
        # 2) Rückkehrmodus: zielgerichtet zum invasiven Nest
        # --------------------------------------------------
        if self.mode == "return":
            target = self.nearest_hill_pos()
            if target is not None:

                def dist2(a, b):
                    dx = a[0] - b[0]
                    dy = a[1] - b[1]
                    return dx * dx + dy * dy

                best = min(neighbors, key=lambda n: dist2(n, target))
                self.model.grid.move_agent(self, best)
                return

        # --------------------------------------------------
        # 3) Suchmodus: aggressivere Exploration
        # --------------------------------------------------
        hill = self.nearest_hill_pos()
        if hill is not None and self.random.random() < 0.6:
            hx, hy = hill

            farther = [
                n for n in neighbors
                if abs(n[0] - hx) + abs(n[1] - hy) >
                abs(self.pos[0] - hx) + abs(self.pos[1] - hy)
            ]

            if farther:
                self.model.grid.move_agent(self, self.random.choice(farther))
                return

        # --------------------------------------------------
        # 4) Fallback: Random Walk
        # --------------------------------------------------
        self.model.grid.move_agent(self, self.random.choice(neighbors))

        
    def eat(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        patches = [a for a in cellmates if isinstance(a, ResourcePatch)]
        if not patches:
            return
        patch = patches[0]
        take = min(self.bite_size, patch.amount)
        if take > 0:
            patch.amount -= take
            self.energy += take * 1.1

    def attack_natives(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        natives = [a for a in cellmates if isinstance(a, NativeAnt)]
        for ant in natives:
            if self.random.random() < self.attack_prob:
                ant.die()

    def die(self):
        self.model.grid.remove_agent(self)
        self.remove()
        
    def deposit_food(self):
        """
        Wenn die Ameise sich auf einem Feld mit einem InvaasiveAntHill befindet,
        lagert sie einen Teil ihrer Energie als Nahrung in den Hügel ein.
        """
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        hills = [a for a in cellmates if isinstance(a, InvasiveAntHill)]
        if not hills:
            return

        hill = hills[0]

        # Nur Energie oberhalb eines Mindestpuffers kann eingelagert werden
        available = max(0.0, self.energy - self.min_energy)
        if available <= 0.0:
            return
        accepted = hill.receive_food(available)
        if accepted > 0:
            self.energy -= accepted
            self.mode = "search"
        
        
    def step(self):
        self.energy -= self.metabolism
        if self.energy <= 0:
            self.die()
            return
        
        self.move()
        self.eat()
        # keine Selbst-Reproduktion mehr
        self.deposit_food()
        
    

    def nearest_hill_pos(self):
        """
        Finde die Position des nächstgelegenen NativeAntHill (falls vorhanden).
        Berücksichtigt torus-Grid.
        """
        from ants_invasion_model import InvasiveAntHill  # falls oben nicht importiert

        hills = self.model.agents_by_type.get(InvasiveAntHill, [])
        if not hills:
            return None

        x, y = self.pos
        width, height = self.model.width, self.model.height

        best_pos = None
        best_d2 = None

        for hill in hills:
            hx, hy = hill.pos
            dx = min(abs(hx - x), width - abs(hx - x))
            dy = min(abs(hy - y), height - abs(hy - y))
            d2 = dx * dx + dy * dy
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                best_pos = (hx, hy)

            return best_pos
        # 💡 Wenn genug Energie: versuche, in Richtung nächster Ameisenhügel zu laufen
        if self.energy >= self.return_threshold:
            target = self.nearest_hill_pos()
            if target is not None:
                tx, ty = target
                width, height = self.model.width, self.model.height

                def torus_dist2(a, b):
                    (x1, y1) = a
                    (x2, y2) = b
                    dx = min(abs(x1 - x2), width - abs(x1 - x2))
                    dy = min(abs(y1 - y2), height - abs(y1 - y2))
                    return dx * dx + dy * dy

                # Wähle die Nachbarzelle, die den Abstand zum Ziel minimiert
                best_cells = []
                best_d2 = None
                for n in neighbors:
                    d2 = torus_dist2(n, target)
                    if best_d2 is None or d2 < best_d2:
                        best_d2 = d2
                        best_cells = [n]
                    elif d2 == best_d2:
                        best_cells.append(n)

                new_pos = self.random.choice(best_cells)
                self.model.grid.move_agent(self, new_pos)
                return

        good_patches = [a for a in neighbor_agents if isinstance(a, ResourcePatch) and a.amount >= self.model.min_food_to_move ]

        if good_patches:
            patch = self.random.choice(good_patches)
            new_pos = patch.pos
            self.model.grid.move_agent(self,new_pos)
            return

        # sonst: normales zufälliges Umherwandern
        new_pos = self.random.choice(neighbors)
        self.model.grid.move_agent(self, new_pos)

        self.move()
        self.eat()
        self.attack_natives()


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
        attack_prob: float = 0.4,
        # Umwelt / Stocks
        habitat_quality_start: float = 1.0,     # 1.0 = 100 %
        warming_start: float = 0.0,            # ΔT in °C
        warming_rate: float = 0.02,            # Zunahme pro Schritt
        climate_habitat_loss: float = 0.005,   # Habitatverlust nur durch Klima / Schritt
        invasive_habitat_impact: float = 0.001,  # zusätzl. Verlust pro invasiver Ameise / Schritt
        n_native_hills: int = 1,
        n_invasive_hills: int = 1,
        seed: Optional[int] = 42,
        min_food_to_move: float =  1.0,

    ):
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=False)

        # Globale Stocks
        self.habitat_quality = habitat_quality_start
        # (0..1-Skala)
        self.warming = warming_start
        self.warming_rate = warming_rate
        self.climate_habitat_loss = climate_habitat_loss
        self.invasive_habitat_impact = invasive_habitat_impact
        
        self.min_food_to_move = min_food_to_move

        self.attack_prob = attack_prob
        # Parameter speichern, damit sie vom Hügel genutzt werden können
        self.native_energy = native_energy
        self.invasive_energy = invasive_energy
        self.metabolism_native = metabolism_native
        self.metabolism_invasive = metabolism_invasive
        self.bite_native = bite_native
        self.bite_invasive = bite_invasive
        x_invasive_start_position = random.randrange(width)
        y_invasive_start_position = random.randrange(height)
        
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

        # Ameisenhügel für die NativeAnts
        for _ in range(n_native_hills):
            hill = NativeAntHill(
                model=self,
                stored_food_native=0.0,
                max_new_ants_per_step=2,
            )
            x = 25
            y = 25
            self.grid.place_agent(hill, (x, y))

        # Einheimische Ameisen (Arbeiterinnen, reproduzieren nicht selbst)
        for _ in range(initial_native):
            ant = NativeAnt(
                model=self,
                energy=native_energy,
                metabolism=metabolism_native,
                bite_size=bite_native,
            )
            x = 25 # self.random.randrange(width)
            y = 25 # self.random.randrange(height)
            self.grid.place_agent(ant, (x, y))

        # Ameisenhügel für die InvasiveAnts
        for _ in range(n_invasive_hills):
            hill = InvasiveAntHill(
                model=self,
                stored_food_invasive=0.0,
                max_new_ants_per_step=3,
            )
            x = x_invasive_start_position
            y = y_invasive_start_position
            self.grid.place_agent(hill, (x, y))

        # Invasive Ameisen
        for _ in range(initial_invasive):
            ant = InvasiveAnt(
                model=self,
                energy=invasive_energy,
                metabolism=metabolism_invasive,
                bite_size=bite_invasive,
                attack_prob=attack_prob,
            )
            x = x_invasive_start_position
            y = y_invasive_start_position
            self.grid.place_agent(ant, (x, y))

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "NativeAnts": lambda m: m.count_native(),
                "InvasiveAnts": lambda m: m.count_invasive(),
                "TotalResources": lambda m: m.total_resources(),
                "HabitatQuality": lambda m: float(m.habitat_quality),
                "Warming": lambda m: float(m.warming),
                "StoredFoodNative": lambda m: sum(
                    hill.stored_food_native for hill in m.agents_by_type.get(NativeAntHill, [])
                ),
                "StoredFoodInvasive": lambda m: sum(
                    hill.stored_food_invasive for hill in m.agents_by_type.get(InvasiveAntHill, [])
                ),
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
        inv = self.count_invasive() * 0.0001
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

        # 3) Ameisenhügel (Königin / Reproduktion)
        if NativeAntHill in self.agents_by_type:
            self.agents_by_type[NativeAntHill].do("step")
            
        # 4) Ameisenhügel (Königin / Reproduktion)
        if InvasiveAntHill in self.agents_by_type:
            self.agents_by_type[InvasiveAntHill].do("step")

        # 5) Ressourcen regenerieren
        if ResourcePatch in self.agents_by_type:
            self.agents_by_type[ResourcePatch].do("step")

        # 6) Globale Stocks (Habitat, Erderwärmung) updaten
        self.update_environment()

        # 7) Daten sammeln
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
