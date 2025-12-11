# Systemgrenzen – Ameisenmodell (aktuelles Notebook)

## Zweck des Modells

Das Modell beschreibt, wie sich über 20 Jahre

- die Population der **einheimischen Ameisen** (`Ameisen`),
- die Population der **invasiven Ameisen** (`Invasive Ameisen`),
- die **Habitatsqualität** (`Habitatsqualität`) und
- die **Ressourcen für die invasive Art** (`Ressourcen für invasive Art`)

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
  Index (0–100 %), der sich regeneriert, aber durch **einheimische Ameisen** verbraucht wird. Hohe Ressourcenverfügbarkeit fördert das Wachstum beider Ameisenarten.

**Kernstruktur (vereinfacht):**

- `Ameisen` ↑ → `Ressourcen` ↓ → Wachstum `Invasive Ameisen` ↓  
- `Invasive Ameisen` ↑ → `Habitatsqualität` ↓ → Wachstum `Ameisen` **und** `Invasive Ameisen` ↓  
- Hohe `Habitatsqualität` und hohe `Ressourcen` → stärkeres Wachstum beider Populationen.

---

## Exogene Grössen

- **Erderwärmung (`Erderwärmung`)**  
  - Wird als **exogener Trend** vorgegeben (Temperaturanstieg pro Jahr).  
  - Wirkt ausschließlich negativ auf die `Habitatsqualität` (mehr Erwärmung ⇒ stärkerer jährlicher Qualitätsverlust).  
  - Es gibt **keine Rückkopplung** vom Ameisensystem auf das Klima.

---

## Außerhalb der Systemgrenzen

Nicht explizit modelliert werden:

- **Landnutzungsänderungen** (Forstwirtschaft, Landwirtschaft, Bebauung)
- **Feinde/Prädatoren** der Ameisen
- **detaillierte Nahrungsnetze** (konkrete Beutearten)
- **Managementmaßnahmen** gegen invasive Arten
- **Räumliche Ausbreitung** (z. B. Koloniewanderungen zwischen Patches)

Diese Faktoren werden, falls nötig, nur im Rahmen von Annahmen oder Szenariobeschreibungen qualitativ diskutiert.
