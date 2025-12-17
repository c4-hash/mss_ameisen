# LE3 - Agentenbasierte Systemmodellierung
In dieser Datei werden die Fragen, welche in der LE3 Mini Challenge beschreibung gestellt wurden, beantwortet.

## Simulation
Die Simulation zeigt Native Ameisen (Blaue Quadrate), Invasive Ameisen (Rote Quadrate), Ressourcen (Grüne Quadrate) und die Ameisenhügel der jeweiligen Ameisen (Schwarze Quadrate).

Die Implementierung der Simulation wurde mit Mesa gemacht und das GUI wurde mit Solara erstellt.

## Aufbau

Die Simulaton besteht aus zwei Daten:
- [ant_invasion_viz.py](ant_invasion_viz.py)
- [ants_invasion_model.py](ants_invasion_model.py)

## Ausführen
Um die Simulation auszuführen, muss Solara installiert sein. Wenn Solara installiert ist, kann die Simulation mit folgendem Befehl ausgeführt werden:

**Solara run ant_invasion_viz.py**

Es sollte sich der Browser öffnen und eine grafische Darstellung der Simulation zeigen.

# Modellparameter

    Die breite und höhe, die das modell annimmt. Grösse wurde so bestimmt, dass ein Quadrat 16 m^2 gross ist. Da sich Ameisen bis zu 200 Meter Meter von ihrem Nest wegbewegen, wurde die höhe und breite so gewählt, dass das auch in unserer Simulation möglich wäre. 
    "width": 51 
    "height": 51

    Die Anzahl einheimischer Ameisen, die am Anfang der Simulation existieren. Es wurde eine relativ junge Kolonie von Waldameisen (Formica rufa) als Anfangskolonie genommen.  
    "initial_native": 30,

    Die Anzahl invasiver Ameisen, die am Anfang der Simulation existieren. Es wurde eine komplett neue Kolonie von roter Feuerameisen (Solenopsis Invicta) genommen. 
    "initial_invasive": 5,

    Parameter, der bestimmt, wieviel Prozent der Quadrate Ressourcen besitzen. Wurde auf 1 (100%) gesetzt, da auf einem 16 m^2 Waldbereich, sehr sicher Ressourcen vorkommen.
    "resource_density": 1,

    Maximale Anzahl Ressourcen, die ein Quadrat besitzen kann in Milligramm. Wurde auf 53.8 Kg gesetzt, da dies laut 
    "patch_max": 200000,
    "patch_initial_share": 0,
    "patch_regen": 6,
    "native_energy": 208,
    "invasive_energy": 105,
    "metabolism_native": 0.015,
    "metabolism_invasive": 0.00225,
    "bite_native": 200,
    "bite_invasive": 200,
    "attack_prob": 0.1,
    "habitat_quality_start": 1.0,
    "warming_start": 0.0,
    "warming_rate": 2/((1*365*24*60)/7), # Berechnung Grad pro Step
    "invasive_habitat_impact": 0.0001,
    "seed": 42,