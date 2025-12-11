# ants_invasion_viz.py
# Visualisierung für AntInvasionModel mit Mesa 3 + SolaraViz

from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from ants_invasion_model import (
    AntInvasionModel,
    NativeAnt,
    InvasiveAnt,
    ResourcePatch,
)


# -------------------------------------------------------
# Agent-Portrayal für das Grid
# -------------------------------------------------------

def agent_portrayal(agent):
    # Ressourcen-Patch: Farbe/Transparenz je nach Füllstand, hinter den Ameisen
    if isinstance(agent, ResourcePatch):
        if agent.max_amount > 0:
            frac = max(0.0, min(1.0, agent.amount / agent.max_amount))
        else:
            frac = 0.0

        # Farbstufen je nach Menge
        if frac == 0.0:
            color = "#ffffff"   # weiß / leer
            alpha = 0.0         # unsichtbar
        elif frac < 0.33:
            color = "#ccffcc"   # sehr hellgrün
            alpha = 0.4
        elif frac < 0.66:
            color = "#66cc66"   # mittelgrün
            alpha = 0.6
        else:
            color = "#006600"   # dunkelgrün
            alpha = 0.8

        return {
            "color": color,
            "size": 150,        # konstanter Block
            "marker": "s",      # Quadrat
            "alpha": alpha,
            "zorder": 0,        # HINTER den Ameisen
        }

    # Einheimische Ameise: blau, oben
    if isinstance(agent, NativeAnt):
        return {
            "color": "blue",
            "size": 60,
            "marker": "o",
            "alpha": 0.9,
            "zorder": 1,
        }

    # Invasive Ameise: rot, oben
    if isinstance(agent, InvasiveAnt):
        return {
            "color": "red",
            "size": 60,
            "marker": "o",
            "alpha": 0.9,
            "zorder": 1,
        }

    # Fallback
    return {
        "color": "gray",
        "size": 30,
        "marker": "x",
        "alpha": 0.8,
        "zorder": 1,
    }


# -------------------------------------------------------
# Standard-Parameter für das Modell
# -------------------------------------------------------

model_params = {
    "width": 30,
    "height": 30,
    "initial_native": 30,
    "initial_invasive": 0,
    "resource_density": 0.1,
    "patch_max": 10.0,
    "patch_initial_share": 0.5,
    "patch_regen": 0.05,
    "native_energy": 5.0,
    "invasive_energy": 5.0,
    "metabolism_native": 0.2,
    "metabolism_invasive": 0.2,
    "bite_native": 2,
    "bite_invasive": 2.8,
    "native_repro_base": 0.15,
    "invasive_repro_base": 0.18,
    "repro_threshold_native": 8.0,
    "repro_threshold_invasive": 8.0,
    "attack_prob": 0.4,
    "habitat_quality_start": 1.0,
    "warming_start": 0.0,
    "warming_rate": 0.001,
    "climate_habitat_loss": 0.001,
    "invasive_habitat_impact": 0.0001,
    "seed": 42,
}

# Modellinstanz
model = AntInvasionModel(**model_params)

# -------------------------------------------------------
# Solara-Komponenten
# -------------------------------------------------------

Space = make_space_component(agent_portrayal)
PopPlot = make_plot_component(["NativeAnts", "InvasiveAnts"])
EnvPlot = make_plot_component(["TotalResources"])
HabPlot = make_plot_component(["HabitatQuality", "Warming"])
StoredPlot = make_plot_component(["StoredFood"])

# -------------------------------------------------------
# SolaraViz-Seite
# -------------------------------------------------------

page = SolaraViz(
    model=model,
    components=[Space, PopPlot, EnvPlot, HabPlot, StoredPlot],
    model_params=model_params,
    name="Ant Invasion Model (Native vs Invasive, Habitat, Resources, Warming)",
)
