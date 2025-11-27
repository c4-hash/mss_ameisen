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
        stored_food: float = 0.0,
        food_capacity: float = 200.0,
        reproduce_threshold: float = 20.0,
        max_new_ants_per_step: int = 3,
    ):
        super().__init__(model)
        self.stored_food = float(stored_food)
        self.food_capacity = float(food_capacity)
        self.reproduce_threshold = float(reproduce_threshold)
        self.max_new_ants_per_step = int(max_new_ants_per_step)

    def receive_food(self, amount: float) -> float:
        """
        Ameisen können Nahrung in den Hügel einlagern.
        Gibt die tatsächlich akzeptierte Menge zurück (falls Kapazität begrenzt).
        """
        if amount <= 0.0:
            return 0.0

        free_capacity = self.food_capacity - self.stored_food
        if free_capacity <= 0.0:
            return 0.0

        accepted = min(amount, free_capacity)
        self.stored_food += accepted
        return accepted

    def step(self):
        """
        Königin-Logik: Wenn genug Nahrung gespeichert ist, erzeugt der Hügel neue Ameisen.
        Die Reproduktion hängt außerdem positiv von habitat_quality ab.
        """
        if self.stored_food < self.reproduce_threshold:
            return

        # 0..1 – schlechte Habitatqualität dämpft Reproduktion
        h = max(0.0, min(1.0, self.model.habitat_quality))
        if h <= 0.0:
            return

        for _ in range(self.max_new_ants_per_step):
            # pro Schritt max_new_ants_per_step neue Ameisen,
            # solange genug Nahrung vorhanden ist
            if self.stored_food < 1.0:
                break

            # neue Arbeiterin erzeugen (Arbeiterinnen reproduzieren nicht selbst)
            ant = NativeAnt(
                model=self.model,
                energy=self.model.native_energy,
                metabolism=self.model.metabolism_native,
                bite_size=self.model.bite_native,
                base_reproduce_prob=self.model.native_repro_base,
                reproduce_threshold=self.model.repro_threshold_native,
            )
            self.model.grid.place_agent(ant, self.pos)

            self.stored_food -= 1.0  # einfache "Kosten" pro neuer Ameise


class NativeAnt(Agent):
    """
    Einheimische Ameise (Arbeiterin einer Kolonie).

    - frisst Ressourcen
    - wird über den Ameisenhügel (Königin) vermehrt (nicht selbst!)
    - kann von invasiven Ameisen getötet/unterdrückt werden
    - läuft bei hoher Energie zum nächstgelegenen NativeAntHill zurück
      und lagert dort Nahrung ein
    """

    def __init__(
        self,
        model: Model,
        energy: float,
        metabolism: float,
        bite_size: float,
        base_reproduce_prob: float,
        reproduce_threshold: float,
        n_workers: int = 200,
        n_males: int = 20,
    ):
        super().__init__(model)
        # Kolonie-Metadaten (informativ; Reproduktion passiert im NativeAntHill)
        self.queen_alive = True
        self.n_workers = int(n_workers)
        self.n_males = int(n_males)

        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        # bleiben als Felder vorhanden, werden aber nicht für Arbeiter-Repro genutzt
        self.base_reproduce_prob = float(base_reproduce_prob)
        self.reproduce_threshold = float(reproduce_threshold)

        # wie viel Energie pro Schritt max. im Hügel eingelagert wird
        self.deposit_rate = 0.5
        # Energiepuffer, damit die Ameise sich nicht komplett "leer" macht
        self.min_energy = 1.0
        self.return_threshold = 6.0          # ab hier lieber heim als weiter fressen
        self.min_food_to_move = 1.0          # mind. Ressourcenmenge, um gezielt hinzulaufen

    # ---------- Verhalten ----------

    def move(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )

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

        # 🔍 sonst: schaue gezielt nach Ressourcenzellen in der Nachbarschaft
        best_cells = []
        best_amount = None
        for n in neighbors:
            cell_agents = self.model.grid.get_cell_list_contents([n])
            patches = [a for a in cell_agents if isinstance(a, ResourcePatch)]
            if not patches:
                continue
            amount = patches[0].amount
            if amount < self.min_food_to_move:
                continue

            if best_amount is None or amount > best_amount:
                best_amount = amount
                best_cells = [n]
            elif amount == best_amount:
                best_cells.append(n)

        if best_cells:
            new_pos = self.random.choice(best_cells)
            self.model.grid.move_agent(self, new_pos)
            return

        # sonst: normales zufälliges Umherwandern
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

        deposit = min(available, self.deposit_rate)
        accepted = hill.receive_food(deposit)
        self.energy -= accepted

    def die(self):
        # wenn du willst, könntest du hier auch n_workers-- einer Kolonie zählen
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
        self.deposit_food()

    def nearest_hill_pos(self):
        """
        Finde die Position des nächstgelegenen NativeAntHill (falls vorhanden).
        Berücksichtigt torus-Grid.
        """
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


class InvasiveAnt(Agent):
    """
    Invasive Ameise (Kolonie-Proxy).

    - frisst Ressourcen
    - Fortpflanzung hängt positiv von der Ressourcensituation ab
    - tötet einheimische Ameisen mit Wahrscheinlichkeit attack_prob
    - bewegt sich gezielt in Richtung ressourcenreicher Nachbarzellen
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
        n_workers: int = 300,
        n_males: int = 30,
    ):
        super().__init__(model)
        # Kolonie-Metadaten
        self.queen_alive = True
        self.n_workers = int(n_workers)
        self.n_males = int(n_males)

        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        self.base_reproduce_prob = float(base_reproduce_prob)
        self.reproduce_threshold = float(reproduce_threshold)
        self.attack_prob = float(attack_prob)

    # ---------- FOOD-SEARCH AI ----------

    def _best_resource_neighbor(self):
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True
        )

        best_cells = []
        best_score = -1.0

        for cell in neighbors:
            cell_agents = self.model.grid.get_cell_list_contents([cell])
            patches = [a for a in cell_agents if isinstance(a, ResourcePatch)]
            if patches:
                base = patches[0].amount
            else:
                base = 0.0

            # leichtes Rauschen, damit sie nicht komplett deterministisch sind
            score = base + self.random.random() * 0.1

            if score > best_score:
                best_score = score
                best_cells = [cell]
            elif score == best_score:
                best_cells.append(cell)

        if not best_cells:
            best_cells = neighbors

        return self.random.choice(best_cells)

    # ---------- Verhalten ----------

    def move(self):
        new_pos = self._best_resource_neighbor()
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
                n_workers=max(80, self.n_workers // 2),
                n_males=max(8, self.n_males // 4),
            )
            self.model.grid.place_agent(child, self.pos)

    def die(self):
        self.queen_alive = False
        self.n_workers = 0
        self.n_males = 0
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
        n_native_hills: int = 1,
        seed: Optional[int] = 42,
    ):
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)
        self.min_food_to_move = 1.0

        # Globale Stocks
        self.habitat_quality = habitat_quality_start
        # (0..1-Skala)
        self.warming = warming_start
        self.warming_rate = warming_rate
        self.climate_habitat_loss = climate_habitat_loss
        self.invasive_habitat_impact = invasive_habitat_impact

        # Parameter speichern, damit sie vom Hügel genutzt werden können
        self.native_energy = native_energy
        self.invasive_energy = invasive_energy
        self.metabolism_native = metabolism_native
        self.metabolism_invasive = metabolism_invasive
        self.bite_native = bite_native
        self.bite_invasive = bite_invasive
        self.native_repro_base = native_repro_base
        self.invasive_repro_base = invasive_repro_base
        self.repro_threshold_native = repro_threshold_native
        self.repro_threshold_invasive = repro_threshold_invasive

        # Ressourcen-Patches
        self.initial_total_resources = 0.0
        for x in range(width):
            for y in range(height):
                if random.randint(1, 10) == 1:
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
                stored_food=0.0,
                food_capacity=200.0,
                reproduce_threshold=20.0,
                max_new_ants_per_step=3,
            )
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(hill, (x, y))

        # Einheimische Ameisen (Arbeiterinnen, reproduzieren nicht selbst)
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
                "StoredFood": lambda m: sum(
                    hill.stored_food for hill in m.agents_by_type.get(NativeAntHill, [])
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

        # 3) Ameisenhügel (Königin / Reproduktion)
        if NativeAntHill in self.agents_by_type:
            self.agents_by_type[NativeAntHill].do("step")

        # 4) Ressourcen regenerieren
        if ResourcePatch in self.agents_by_type:
            self.agents_by_type[ResourcePatch].do("step")

        # 5) Globale Stocks (Habitat, Erderwärmung) updaten
        self.update_environment()

        # 6) Daten sammeln
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
