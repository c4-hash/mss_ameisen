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

    Die breite und höhe, die das modell annimmt. Grösse wurde so bestimmt, dass ein Quadrat 16 m² gross ist. Da sich Ameisen bis zu 200 Meter Meter von ihrem Nest wegbewegen, wurde die höhe und breite so gewählt, dass das auch in unserer Simulation möglich wäre. 
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

# Backtest

Auf einen Backtest wird aus zeitlichen Gründen nicht durchgeführt.

# Erkenntnisse

In unserem Modell entwickeln sich die beiden Ameisenpopulationen parallel. Jedoch durch den klimatischen Einfluss und die invasiven Ameisen, wird die Habitatsqualität über die Zeit verschlechtert. Dadurch sterben die nativen Ameisen nach kurzer Zeit aus.

# Fragen laut Mini Challenge

Hier werden die Fragen beantwortet, die bei der Mini-Challenge Aufgabenstellung gefragt waren.

## Problemstellung

Was für Auswirkungen hat eine invasive Ameisenart auf unsere nativen Ameisen?

## Kenngrössen

Siehe Modellparameter

## Systemgrenzen

- Native Ameisenart der Schweiz
- Einzelne invasive Art die bereits in der Schweiz lebt
- Habitatsqualität (Klimaerwärmung mit der Annahme, dass pro Jahr die Durchschnitttemperatur um 0.02°C steigt und Anstieg der Anzahl invasiven Ameisen)
- Ressourcen

### Außerhalb der Systemgrenzen

Nicht explizit modelliert werden:

- Landnutzungsänderungen (Forstwirtschaft, Landwirtschaft, Bebauung)
- Feinde/Prädatoren der Ameisen
- Detaillierte Nahrungsnetze (konkrete Beutearten)
- Räumliche Ausbreitung (z. B. Koloniewanderungen zwischen Patches)

Diese Faktoren werden, falls nötig, nur im Rahmen von Annahmen oder Szenariobeschreibungen qualitativ diskutiert.

## Mikroebene (Agentenebene)

- Bewegung einzelner Arbeiterinnen (Schrittweise Fortbewegung, Orientierung)
- Entscheidungen: suchen / folgen / umkehren / tragen / abgeben
- Lokale Interaktionen: Ameise–Ameise, Ameise–Ressource

## Makroebene (Systemebene)
- Koloniegrößen (Anzahl Arbeiterinnen/Brut), Gesamtenergie-/Futtervorrat
- Netto-Eintrag vs. Verbrauch --> Wachstum oder Schrumpfen
- Räumliche Muster: Ausbeutung des Gebiets
- Stabilität/Resilienz bei Störungen (Ressourcenpuls, Konkurrenz)

## Räumliche Auflösung

Wir haben ein 2D-Gitter mit Koordinaten. Die breite und höhe, die das modell annimmt. Grösse wurde so bestimmt, dass ein Quadrat 16 m² gross ist. Da sich Ameisen bis zu 200 Meter Meter von ihrem Nest wegbewegen, wurde die höhe und breite so gewählt, dass das auch in unserer Simulation möglich wäre. 

## Distanzfunktion

Wir verwenden die Manhatten-Distanz um mit Entfernungen zu rechnen.

## Agenten & Interaktionen

- Native Ameisenarbeiterinnen
- Nativer Ameisenhügel in der Mitte des Gitters
- Invasive Ameisenarbeiterinnen
- Invasiver Ameisenhügel an einer random Position
- Ressourcen

### Interaktionen

- Invasive Arten greifen native an
- Invasive und native verwenden Ressourcen für Energie
- Invasive und native bringen die nicht verwendeten Ressourcen zurück zum Ameisenhügel
- Invasive und native Ameisenhügel generieren neue Ameisen mit gespeicherten Ressourcen

### Eigenschaften

- Arbeiterinnen: Position, Energiezustand, Modus (Suchen/Return)
- Nahrung: Menge, Regeneration
- Ameisenhaufen: Eiablagerate, gespeicherte Nahrung

## Zeithorizont

Mit jedem Step vergehen 7 Minuten.

### Begründung
Native laufen durchschnitlich 1 cm/s und invasive 1.2 cm/s. Um das ganze zu vereinfachen haben wir die Annahme getroffen, dass beide Arten gleich schnell laufen und zwar 1 cm/s.

## Externe Grösse
Als externe Grösse haben wir in unserem Modell den Klimawandel. Der Klimawandel beeinflusst die Habitatsqualität welche wiederum die Generationsrate der nativen Ameisen reduziert. 

## Anfangsparameter

Siehe Modellparameter

## Kenngrössen Entwicklung

Die nativen Ameisen sterben aus und die Invasiven wachsen stetig. Die Habitatsqualität sinkt und die Erwärmung steigt gleichmässig.

## Backtest

Wir konnten keinen Backtest machen aber wenn wir einen machen würden, würden wir andere invasive Spezies anschauen wie diese mit den Nativen interagieren.