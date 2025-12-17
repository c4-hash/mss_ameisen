# ants_abm_mesa.py
# Mesa-3-kompatibles Beispiel:
# Ameisen bewegen sich auf einem Grid und fressen Ressourcen.
# Läuft ohne Web-GUI, gibt Kennzahlen auf der Konsole aus.

from __future__ import annotations
from typing import Optional

from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


# --------------------------------------
# ResourcePatch-Agent
# --------------------------------------

class ResourcePatch(Agent):
    """
    Passiver Ressourcen-Patch mit bestimmter Menge an Nahrung,
    der optional pro Schritt regeneriert.
    """

    def __init__(self, model: Model, amount: float, max_amount: float, regen_rate: float):
        # Mesa 3: nur model übergeben, unique_id wird automatisch vergeben
        super().__init__(model)
        self.amount = float(amount)
        self.max_amount = float(max_amount)
        self.regen_rate = float(regen_rate)

    def step(self):
        if self.regen_rate <= 0:
            return
        self.amount = min(self.max_amount, self.amount + self.regen_rate)


# --------------------------------------
# Ant-Agent
# --------------------------------------

class Ant(Agent):
    """
    Einfache Ameise:
    - bewegt sich zufällig
    - frisst Ressourcen, wenn sie welche findet
    - verliert pro Schritt Energie (metabolism)
    - kann sich bei hoher Energie reproduzieren
    - stirbt bei Energie <= 0
    """

    def __init__(
        self,
        model: Model,
        energy: float,
        metabolism: float,
        bite_size: float,
        reproduce_threshold: float,
        reproduce_prob: float,
    ):
        super().__init__(model)
        self.energy = float(energy)
        self.metabolism = float(metabolism)
        self.bite_size = float(bite_size)
        self.reproduce_threshold = float(reproduce_threshold)
        self.reproduce_prob = float(reproduce_prob)

    def move(self):
        # Moore-Nachbarschaft (inklusive aktueller Zelle)
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
        if self.energy >= self.reproduce_threshold and \
                self.random.random() < self.reproduce_prob:

            child_energy = self.energy * 0.5
            self.energy *= 0.5

            child = Ant(
                model=self.model,
                energy=child_energy,
                metabolism=self.metabolism,
                bite_size=self.bite_size,
                reproduce_threshold=self.reproduce_threshold,
                reproduce_prob=self.reproduce_prob,
            )
            # Agent registriert sich beim Model automatisch
            self.model.grid.place_agent(child, self.pos)

    def step(self):
        # Energieverlust
        self.energy -= self.metabolism
        if self.energy <= 0:
            # Mesa 3: sauber entfernen über self.remove()
            self.remove()
            return

        self.move()
        self.eat()
        self.maybe_reproduce()


# --------------------------------------
# Model
# --------------------------------------

class AntForageModel(Model):
    """
    Ameisen-Futtersuche-Modell:
    - MultiGrid mit ResourcePatch in jeder Zelle
    - einige Ameisen, die Ressourcen fressen und sich vermehren
    """

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        initial_ants: int = 30,
        resource_density: float = 0.5,   # Anteil Zellen mit Startressourcen
        patch_max: float = 10.0,
        patch_initial_share: float = 0.6,  # Anteil von max beim Start
        patch_regen: float = 0.05,       # Regeneration pro Schritt
        ant_energy: float = 5.0,
        ant_metabolism: float = 0.2,
        ant_bite: float = 1.0,
        ant_reproduce_threshold: float = 8.0,
        ant_reproduce_prob: float = 0.15,
        seed: Optional[int] = 42,
    ):
        # Mesa-3-konforme Initialisierung
        super().__init__(seed=seed)

        self.width = width
        self.height = height
        self.grid = MultiGrid(width, height, torus=True)

        # --------- Resource Patches erzeugen (ohne coord_iter) ----------
        for x in range(width):
            for y in range(height):
                has_resource = self.random.random() < resource_density
                amount = patch_max * patch_initial_share if has_resource else 0.0

                patch = ResourcePatch(
                    model=self,
                    amount=amount,
                    max_amount=patch_max,
                    regen_rate=patch_regen,
                )
                self.grid.place_agent(patch, (x, y))

        # --------- Ameisen erzeugen ----------
        for _ in range(initial_ants):
            ant = Ant(
                model=self,
                energy=ant_energy,
                metabolism=ant_metabolism,
                bite_size=ant_bite,
                reproduce_threshold=ant_reproduce_threshold,
                reproduce_prob=ant_reproduce_prob,
            )
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(ant, (x, y))

        # --------- DataCollector ----------
        self.datacollector = DataCollector(
            model_reporters={
                "Ants": lambda m: m.count_ants(),
                "TotalResources": lambda m: m.total_resources(),
                "MeanEnergy": lambda m: m.mean_ant_energy(),
            }
        )

    # ---- Kennzahlen-Hilfsfunktionen ------------------------

    def count_ants(self) -> int:
        if Ant not in self.agents_by_type:
            return 0
        return len(self.agents_by_type[Ant])

    def total_resources(self) -> float:
        if ResourcePatch not in self.agents_by_type:
            return 0.0
        return sum(p.amount for p in self.agents_by_type[ResourcePatch])

    def mean_ant_energy(self) -> float:
        if Ant not in self.agents_by_type or len(self.agents_by_type[Ant]) == 0:
            return 0.0
        energies = [a.energy for a in self.agents_by_type[Ant]]
        return sum(energies) / len(energies)

    # ---- Simulationsschritt ------------------------

    def step(self):
        # Aktivierungsmuster über AgentSet-API:
        # 1) Ameisen in zufälliger Reihenfolge
        if Ant in self.agents_by_type:
            self.agents_by_type[Ant].shuffle_do("step")
        # 2) Danach Patches (Regeneration)
        if ResourcePatch in self.agents_by_type:
            self.agents_by_type[ResourcePatch].do("step")

        self.datacollector.collect(self)


# --------------------------------------
# Run
# --------------------------------------

if __name__ == "__main__":
    model = AntForageModel()

    n_steps = 50
    for step in range(n_steps):
        model.step()
        print(
            f"Step {step:3d} | "
            f"Ants = {model.count_ants():3d} | "
            f"TotalResources = {model.total_resources():7.2f} | "
            f"MeanEnergy = {model.mean_ant_energy():5.2f}"
        )

    print("\nLetzte 5 Zeilen der gesammelten Daten:")
    print(model.datacollector.get_model_vars_dataframe().tail())
