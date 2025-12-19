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

**Ordner:** [SystemModellierungen & LE1](SystemModellierungen_&_LE1/)

Enthält die Artefakte aus LE1:

- [Causal_loop_Simplified.drawio](SystemModellierungen_&_LE1/Causal_loop_Simplified.drawio) / [Causal_loop.drawio.png](SystemModellierungen_&_LE1/Causal_loop.drawio.png)  
  Vereinfachtes Kausalschleifen-Diagramm mit **1 Loop**:
  - Ameisenpopulation → Ressourcen für invasive Art → invasive Arten → Habitatqualität → Ameisenpopulation
- [Stakeholder_Diagramm.drawio](SystemModellierungen_&_LE1/Stakeholder_Diagramm.drawio)  
  Stakeholder-Map für diesen Loop (Ameisen, invasive Arten).
- [mini_power_interest_raster_reduced.png](SystemModellierungen_&_LE1/mini_power_interest_raster_reduced.png)
  Reduziertes Power-Interest-Raster für die wichtigsten Stakeholder.
- [Systemgrenzen.md](SystemModellierungen_&_LE1/Systemgrenzen.md)
  Textliche Definition der Systemgrenzen (Raum: lokales Wald-/Saumbiotop, Zeit: 20 Jahre, endogene Variablen, exogener Treiber Erderwärmung).

Diese Artefakte werden in LE2–LE4 weiterverwendet.

---

### LE 2 – Systemdynamiksimulation (BPTK-Py)


**Ort:** [Causal_loop_Simplified.drawio](SystemModellierungen_&_LE1/Causal_loop_Simplified.drawio) - Abschnitt **„LE 2“**


Inhalt:


- Die umgesetzte Kaussalschleife inkl. Fragestellung


**Ort:** [Ameisen_SD_BPTK.ipynb](LE2_&_LE4/Ameisen_SD_BPTK.ipynb) – Abschnitt **„LE 2: Systemdynamiksimulationen“**

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

- [LE3.md](LE3/LE3.md)

  Beschreibt die Simulation und beantwortet Fragen der Mini Challenge

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


**Ort:** [Causal_loop_Simplified.drawio](SystemModellierungen_&_LE1/Causal_loop_Simplified.drawio) - Abschnitt **„LE 4“**


Inhalt:


- Die umgesetzte Kaussalschleife inkl. Fragestellung und der Übertragungskanäle


**Ort:** [Ameisen_SD_BPTK.ipynb](LE2_&_LE4/Ameisen_SD_BPTK.ipynb) – Abschnitt **„LE 4: Szenarien“**

Inhalt:

- Definition eines `scenario_manager` für **verschiedene Erwärmungsszenarien**  
  (z.B. jährliche Temperaturzunahme von 0.05, 0.10, 0.15 °C).
- Die Szenarien verändern den exogenen Treiber `Erhöhung pro Jahr`, der die `Erderwärmung` und damit indirekt die `Habitatsqualität` und die Ameisenpopulation beeinflusst.
- BPTK-Py-Plot vergleicht die resultierenden Ameisenpopulationen über 20 Jahre für die verschiedenen Szenarien.

---

## Repository-Struktur (Kurzüberblick)

```text
.
├── LE2 & LE4/
│   └── Ameisen_SD_BPTK.ipynb      # LE2 & LE4 – Systemdynamik + Szenarien
├── LE3/
│   ├── ants_invasion_model.py     # LE3 - Mesa Modell
│   ├── ant_invasion_viz.py        # LE3 - Solara visualisierung
|   ├── LE3.md
|   └── Old # Tests mit Mesa und Solara
|       ├── LE3.ipynb
|       ├── ants_abm_mesa.py
|       └── ants_viz.py
├── SystemModellierungen & LE1/
│   ├── Causal_loop.drawio
│   ├── Causal_loop.drawio.png
│   ├── Causal_loop_Simplified.drawio
│   ├── Stakeholder_Diagramm.drawio
│   ├── mini_power_interest_raster_reduced.png
│   └── Systemgrenzen.md
├── pyproject.toml                 # Python-Projektkonfiguration (u.a. BPTK-Py, Mesa)
├── poetry.lock
└── bptk_py.log                    # Log von BPTK-Py (kann ignoriert werden)



## Poetry Setup (Kurzanleitung)

### 1. Poetry installieren (Windows/PowerShell)

Falls pipx nicht installiert ist wird `pipx` installiert, um Poetry verfügbar zu machen:

```powershell
python -m pip install --user pipx
python -m pipx ensurepath
```
Poetry install via pipx

```powershell
pipx install poetry
poetry --version
```

### 2. Projekt installieren

Dieser Befehl erstellt automatisch die virtuelle Umgebung (Env) und installiert alle Abhängigkeiten:

```powershell
poetry install
```

> **Hinweis bei Fehlern:**
> Falls es Probleme mit der `pyproject.toml` oder dem Lockfile gibt (Versionskonflikte), hilft meist das Neuschreiben des Lockfiles:
>
> ```powershell
> poetry lock
> poetry install
> ```