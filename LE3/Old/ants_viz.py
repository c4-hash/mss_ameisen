# ants_viz.py
# Visualisierung für AntForageModel mit Mesa 3 + SolaraViz

from mesa.visualization import SolaraViz, make_space_component, make_plot_component

from LE3.Old.ants_abm_mesa import AntForageModel, Ant, ResourcePatch


# ---------------------------
# Agent-Darstellung
# ---------------------------

def agent_portrayal(agent):
    # Ressourcen-Patch: Farbe/Größe nach Menge
    if isinstance(agent, ResourcePatch):
        if agent.max_amount > 0:
            frac = max(0.0, min(1.0, agent.amount / agent.max_amount))
        else:
            frac = 0.0

        size = 10 + 40 * frac  # 10 .. 50

        return {
            "color": "green",   # matplotlib/altair-Farbnamen gehen
            "size": size,       # Marker-Größe
            "marker": "s",      # Quadrat
            "alpha": 0.6,
        }

    # Ameise: schwarzer Punkt
    if isinstance(agent, Ant):
        return {
            "color": "black",
            "size": 50,
            "marker": "o",      # Kreis
            "alpha": 1.0,
        }

    # Fallback (sollte kaum auftauchen)
    return {
        "color": "gray",
        "size": 20,
        "marker": "x",
        "alpha": 0.8,
    }


# ---------------------------
# Modell-Parameter wie im Skript
# (alle Werte sind "fixed", keine Slider)
# ---------------------------

model_params = {
    "width": 20,
    "height": 20,
    "initial_ants": 30,
    "resource_density": 0.5,
    "patch_max": 10.0,
    "patch_initial_share": 0.6,
    "patch_regen": 0.05,
    "ant_energy": 5.0,
    "ant_metabolism": 0.2,
    "ant_bite": 1.0,
    "ant_reproduce_threshold": 8.0,
    "ant_reproduce_prob": 0.15,
    "seed": 42,
}

# Modellinstanz mit diesen Parametern
model = AntForageModel(**model_params)

# Space-Komponente (Grid) + Zeitreihen-Plot
Space = make_space_component(agent_portrayal)
Plot = make_plot_component(["Ants", "TotalResources", "MeanEnergy"])

# SolaraViz-Seite – das ist das Objekt, das Solara anzeigt
page = SolaraViz(
    model=model,
    components=[Space, Plot],
    model_params=model_params,
    name="Ant Foraging Model",
)
