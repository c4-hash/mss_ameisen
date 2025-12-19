# mss Mini Challenge – Ameisen & invasive Arten

Dieses Repository enthält die Artefakte für alle vier Mini-Challenges (LE1–LE4) des Moduls **mss – Modellierung und Simulation dynamischer Systeme**.  
Thema ist die Dynamik zwischen einheimischen Ameisen, invasiven Ameisen, Habitatqualität und Klimawandel.

Im Fokus stehen:

- Systemkarte (Causal Loop, Stakeholder, Systemgrenzen)
- Systemdynamik-Modell mit BPTK-Py
- Agentenbasierte Simulation mit Mesa
- Szenarien zur Erderwärmung und deren Wirkung auf das System

---

## Lern­einheiten und Inhalte

### LE 1 – Systemkarte & Systemgrenzen

**Ordner:** [SystemModellierungen](SystemModellierungen/)

Enthält die Artefakte aus LE1:

- [Causal_loop_Simplified.drawio](SystemModellierungen/Causal_loop_Simplified.drawio) / [Causal_loop.drawio.png](SystemModellierungen/Causal_loop.drawio.png)  
  Vereinfachtes Kausalschleifen-Diagramm mit **1 Loop**:
  - Ameisenpopulation → Ressourcen für invasive Art → invasive Arten → Habitatqualität → Ameisenpopulation
- [Stakeholder_Diagramm.drawio](SystemModellierungen/Stakeholder_Diagramm.drawio)  
  Stakeholder-Map für diesen Loop (Ameisen, invasive Arten).
- [mini_power_interest_raster_reduced.png](SystemModellierungen/mini_power_interest_raster_reduced.png)
  Reduziertes Power-Interest-Raster für die wichtigsten Stakeholder.
- [Systemgrenzen.md](SystemModellierungen/Systemgrenzen.md)
  Textliche Definition der Systemgrenzen (Raum: lokales Wald-/Saumbiotop, Zeit: 20 Jahre, endogene Variablen, exogener Treiber Erderwärmung).

Diese Artefakte werden in LE2–LE4 weiterverwendet.

---

### LE 2 – Systemdynamiksimulation (BPTK-Py)


**Ort:** [Causal_loop_Simplified.drawio](SystemModellierungen/Causal_loop_Simplified.drawio) - Abschnitt **„LE 2“**


Inhalt:


- Die umgesetzte Kaussalschleife inkl. Fragestellung


**Ort:** [Ameisen_SD_BPTK.ipynb](Notebooks/Ameisen_SD_BPTK.ipynb) – Abschnitt **„LE 2: Systemdynamiksimulationen“**

Inhalt:

- **Stocks (Bestände):**
  - `Ameisen` – einheimische Ameisenpopulation
  - `Invasive Ameisen` – Population der invasiven Art
  - `Habitatsqualität` – Habitatqualität in %
  - `Ressourcen` – Ressourcenverfügbarkeit (v.a. für invasive Arten) in %
  - `Erderwärmung` – aktueller Temperaturstand (°C)
  - `Erhöhung pro Jahr` – jährliche Temperaturzunahme (°C/Jahr)

- **Flows (Flüsse):**
  - Wachstum/Verlust Ameisen (`Wachstum Ameisen`, `Verlust Ameisen`)
  - Wachstum/Verlust Invasive (`Wachstum Invasive Ameisen`, `Verlust Invasive Ameisen`)
  - Unterdrückung der einheimischen Ameisen durch invasive (`Unterdrückung Ameisen durch Invasive`)
  - Habitatverlust / -regeneration (`Habitatverlust`, `Veränderung Habitat`, `Regeneration Habitat`)
  - Ressourcenverbrauch / -regeneration (`Ressourcenverbrauch`, `Regeneration Ressourcen`)

- **Klimatreiber:**  
  `Erderwärmung` wirkt negativ auf die `Habitatsqualität`, gesteuert über `Erhöhung pro Jahr` (exogener Parameter).

- **Plots:**  
  Zeitreihen für Ameisen, invasive Ameisen, Habitatqualität, Ressourcen und Erderwärmung werden mit BPTK-Py geplottet.

---

### LE 3 – Agentenbasierte Modellierung (Mesa)

**Ordner:** [LE3](LE3/)

Inhalt:
- [ant_invasion_viz.py](LE3/ant_invasion_viz.py), [ants_viz.py](LE3/ants_viz.py)
  Visualisierungen (z.B. Grid-Darstellung, Zeitreihen).
  
- [ant_invasion_model.py](LE3/ant_invasion_model.py)  
  Mesa-Modelldefinition (Grid, Agenten, Interaktionen).

- [Old](LE3/Old)
  Order für alte Testdateien

- [LE3.ipynb](LE3/Old/LE3.ipynb) 
  Test-Notebook für die agentenbasierte Simulation.

- [ants_abm_mesa.py](LE3/Old/ants_abm_mesa.py) 
  Test Python Datei für erste Schritte mit Mesa und Ameisen

- [ants_viz.py](LE3/Old/ants_viz.py) 
  Test Python Datei für erste Schritte mit Solara

Die Simulation kann mit solara run LE3/ant_invasion_viz.py ausgeführt werden

Hier wird die Mikro-Ebene (einzelne Ameisen / Kolonien) modelliert und mit der Makro-Dynamik aus LE1/LE2 verknüpft.

---

### LE 4 – Szenarien & integrierte Analyse


**Ort:** [Causal_loop_Simplified.drawio](SystemModellierungen/Causal_loop_Simplified.drawio) - Abschnitt **„LE 4“**


Inhalt:


- Die umgesetzte Kaussalschleife inkl. Fragestellung und der Übertragungskanäle


**Ort:** [Ameisen_SD_BPTK.ipynb](Notebooks/Ameisen_SD_BPTK.ipynb) – Abschnitt **„LE 4: Szenarien“**

Inhalt:

- Definition eines `scenario_manager` für **verschiedene Erwärmungsszenarien**  
  (z.B. jährliche Temperaturzunahme von 0.05, 0.10, 0.15 °C).
- Die Szenarien verändern den exogenen Treiber `Erhöhung pro Jahr`, der die `Erderwärmung` und damit indirekt die `Habitatsqualität` und die Ameisenpopulation beeinflusst.
- BPTK-Py-Plot vergleicht die resultierenden Ameisenpopulationen über 20 Jahre für die verschiedenen Szenarien.

---

## Repository-Struktur (Kurzüberblick)

```text
.
├── Notebooks/
│   └── Ameisen_SD_BPTK.ipynb      # LE2 & LE4 – Systemdynamik + Szenarien
├── LE3/
│   ├── ants_invasion_model.py     # LE3 - Mesa Modell
│   └── ant_invasion_viz.py        # LE3 - Solara visualisierung
|   └── Old # Tests mit Mesa und Solara
|       ├── LE3.ipynb
|       ├── ants_abm_mesa.py
|       └── ants_viz.py
├── SystemModellierungen/
│   ├── Causal_loop.drawio
│   ├── Causal_loop.drawio.png
│   ├── Causal_loop_Simplified.drawio
│   ├── Stakeholder_Diagramm.drawio
│   ├── mini_power_interest_raster_reduced.png
│   └── Systemgrenzen.md
├── pyproject.toml                 # Python-Projektkonfiguration (u.a. BPTK-Py, Mesa)
├── poetry.lock
└── bptk_py.log                    # Log von BPTK-Py (kann ignoriert werden)
