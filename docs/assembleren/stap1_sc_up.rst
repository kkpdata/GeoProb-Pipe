Stap 1: Scenarioberekeningen → uittredepunt
=============================================

In GeoProb‑Pipe vormt het **uittredepunt** de kleinste zelfstandige
bouwsteen in de assemblage van faalkansen. Een uittredepunt is een
fysieke locatie langs de waterkering waar piping kan initiëren.
In tegenstelling tot de klassieke BOI‑benadering wordt geen 
enkele doorsnede beschouwd, maar een reeks uittredepunt locaties langs
het traject.

Per uittredepunt worden meerdere ondergrondscenario’s doorgerekend.
In stap 0 levert dit voor elk scenario één β‑waarde op.

Van scenarioberekening naar de betrouwbaarheid van het uittredepunt
--------------------------------------------------------------------

Stap 0 levert één β‑waarde per uittredepunt per
ondergrondscenario. Deze waarden worden vervolgens samengevoegd tot één
β‑waarde per uittredepunt door de faalkansen te wegen met de kans van
het scenario.

De faalkansen uit de scenarioberekeningen worden gecombineerd via een
gewogen gemiddelde, waarbij elke scenariokans als wegingsfactor wordt
gebruikt.

Als één scenarioberekening niet convergeert, dan convergeert het
uittredepunt als geheel ook niet.

