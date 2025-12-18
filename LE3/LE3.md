# LE3 - Agentenbasierte Systemmodellierung
In dieser Datei werden die Fragen, welche in der LE3 Mini Challenge beschreibung gestellt wurden, beantwortet.

## Simulation
Die Simulation zeigt Native Ameisen (Blaue Quadrate), Invasive Ameisen (Rote Quadrate), Ressourcen (Grüne Quadrate) und die Ameisenhügel der jeweiligen Ameisen (Schwarze Quadrate).

Die Implementierung der Simulation wurde mit Mesa gemacht und das GUI wurde mit Solara erstellt.

Ein Step in der Simulation sind Gleichzusetzen mit 7 Minuten, die vergehen.

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

    Maximale Anzahl Ressourcen, die ein Quadrat besitzen kann in Milligramm. Die Zahl wurde auf 200'000 Mg gesetzt, da das laut verschiedener aggregierter Quellen ein grober Durchschnittswert die Produktion von "Ameisennahrung" (Samen, Insekten, etc.) für ein 4*4 m Feld pro Jahr ist.
    "patch_max": 200000,

    Initialwert der Ressourcen auf einem Ressourcenfeld. Wurde auf 0 gesetzt, da es schwierig war, eine Schätzung für einen guten Anfangswert zu tätigen.
    "patch_initial_share": 0,

    Regenerierungswert der Nahrung auf den Ressourcenfeldern. Wurde auf 6 gesetzt, da das ein hochgerechneter Wert der jährlichen generation auf Sieben Minuten ist.
    "patch_regen": 6,

    Energie der Ameisen. Aufgrund implementation eine Mischung zwischen der theoretisch möglichen "Ameisenenergie" und der Tragekapazität der Ameisen. 
    "native_energy": 208, -> 8 Joule "Ameisentank" + 200 mg Tragekapazität
    "invasive_energy": 105, -> 5 Joule "Ameisentank" + 100 mg Tragekapazität
    
    Metabolismus von den Ameisen
    "metabolism_native": 0.015,
    "metabolism_invasive": 0.00225,
    
    "Bissgrösse" der Ameisen. Gibt an wie viele Mg eine Ameisen pro Step von einem Ressourcenfeld abbeissen kann.
    "bite_native": 200,
    "bite_invasive": 100,

    Warscheinlichkeit, dass invasive Ameisen die Nativen Ameisen attackieren.
    "attack_prob": 0.1,

    Parameter, der bestimmt, wie "gut" das Habitat zu beginn der Simulation ist.
    "habitat_quality_start": 1.0,
    
    Wie viel Klimaerwährmung wird zu anfang der Simulation angenommen.
    "warming_start": 0.0,

    Um wie viel Grad erhöht sich die Klimaerwährmung pro step. Es wird von einer jährlichen Erwärmung von 0.02 Grad pro Jahr ausgegangen. Diese wird dann auf 7 Minuten heruntergebrochen.
    "warming_rate": 0.02/((1*365*24*60)/7), # Berechnung Grad pro Step

    Wert, wie fest die Invasiven Ameisen die Habitatsqualität beeinflussen.
    "invasive_habitat_impact": 0.0001,
    
    "seed": 42,