# Systemgrenzen – Ameisenmodell (aktuelles Notebook)

## Zweck des Modells

Das Modell beschreibt, wie sich über 20 Jahre

- die Population der **einheimischen Ameisen** (`Ameisen`),
- die Population der **invasiven Ameisen** (`Invasive Ameisen`),
- die **Habitatsqualität** (`Habitatsqualität`) und
- die **Ressourcen** (`Ressourcen`)

unter dem Einfluss von **Erderwärmung** und **gegenseitiger Konkurrenz** entwickeln.

Sowohl einheimische als auch invasive Ameisen sind dabei von **Habitatqualität und Ressourcen** abhängig und beeinflussen diese wiederum.

---

## Räumliche und zeitliche Grenzen

- **Raum:** Ein lokales **Wald-/Saumbiotop** (z. B. Waldrand, Wiese am Waldrand).  
  - Keine explizite räumliche Struktur, keine Migration über die Gebietskante.
- **Zeit:** 20 Modelljahre, diskret mit `dt = 0.25` Jahren.

---

## Endogene Grössen (im System)

- **Ameisen (`Ameisen`)**  
  Bestandsgröße der einheimischen Ameisen. Wachstum hängt von  
  `Habitatsqualität` **und** `Ressourcen` ab; sie verbrauchen Ressourcen und werden durch invasive Ameisen verdrängt.

- **Invasive Ameisen (`Invasive Ameisen`)**  
  Bestandsgröße der invasiven Ameisen. Wachstum hängt ebenfalls von  
  `Habitatsqualität` **und** `Ressourcen` ab; sie belasten die `Habitatsqualität` und verdrängen einheimische Ameisen direkt.

- **Habitatsqualität (`Habitatsqualität`)**  
  Index (0–100 %), der sich durch Regeneration verbessert und durch  
  **Erderwärmung** und **invasive Ameisen** verschlechtert. Gute Habitatqualität fördert das Wachstum beider Ameisenarten.

- **Ressourcen für invasive Art (`Ressourcen für invasive Art`)**  
  Index (0–100 %), der sich regeneriert, aber durch **einheimische und invasive Ameisen** verbraucht wird.  
  Hohe Ressourcenverfügbarkeit fördert das Wachstum beider Ameisenarten.


**Kernstruktur (vereinfacht):**

- `Ameisen` ↑ und `Invasive Ameisen` ↑ → `Ressourcen` ↓ → Wachstum beider Populationen ↓  
- `Invasive Ameisen` ↑ → `Habitatsqualität` ↓ → Wachstum `Ameisen` **und** `Invasive Ameisen` ↓  
- `Invasive Ameisen` ↑ → Unterdrückung der `Ameisen` ↑ (saturierend, abhängig von beiden Populationen)

---

## Exogene Grössen

- **Erderwärmung (`Erderwärmung`)**  
  - Wird als **exogener Trend** vorgegeben (Temperaturanstieg pro Jahr; Szenarien z.B. 0.02 / 0.04 / 0.06 °C/Jahr).  
  - Startwert repräsentiert den heutigen globalen Erwärmungsstand (z.B. **1.6 °C über 1850–1900**).  
  - Der zusätzliche jährliche Habitatdruck wird im Modell über die **zusätzliche Erwärmung ab heute** berechnet:  
    **ΔT = max(0, Erderwärmung − 1.6)**.  
  - Es gibt **keine Rückkopplung** vom Ameisensystem auf das Klima.

- **Managementmaßnahmen** gegen invasive Arten  
  - Werden als **exogene Eingriffe** modelliert in erhöhung **invasive_loss** in **LE4 Szenarien**.
---

## Außerhalb der Systemgrenzen

Nicht explizit modelliert werden:

- **Landnutzungsänderungen** (Forstwirtschaft, Landwirtschaft, Bebauung)
- **Feinde/Prädatoren** der Ameisen
- **detaillierte Nahrungsnetze** (konkrete Beutearten)
- **Räumliche Ausbreitung** (z. B. Koloniewanderungen zwischen Patches)

Diese Faktoren werden, falls nötig, nur im Rahmen von Annahmen oder Szenariobeschreibungen qualitativ diskutiert.
