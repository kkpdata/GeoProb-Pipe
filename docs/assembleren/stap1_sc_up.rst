Faalkans uittredepuntniveau
===========================

In GeoProb-Pipe vormt het **uittredepunt** de kleinste zelfstandige bouwsteen in de assemblage van faalkansen. Een
uittredepunt is een fysieke locatie langs de waterkering waar piping kan initiëren. In tegenstelling tot de klassieke
BOI-benadering wordt geen doorsnede beschouwd, maar een reeks uittredepuntlocaties langs het traject.

Per uittredepunt worden meerdere **ondergrondscenario’s** doorgerekend. Stap 0 levert voor elk scenario één
betrouwbaarheidsindex (:math:`\\beta`).

Van scenarioberekening naar de betrouwbaarheid van het uittredepunt
-------------------------------------------------------------------

De resultaten uit de scenarioberekeningen worden samengevoegd tot één faalkans per uittredepunt door de scenariokansen
als wegingsfactor te gebruiken. De gecombineerde faalkans wordt bepaald via een gewogen gemiddelde van de afzonderlijke
scenariokansen.

Indien één van de scenarioberekeningen niet convergeert, wordt het betreffende uittredepunt als **niet geconvergeerd**
beschouwd. Verdere opschaling naar vak- en trajectniveau is in dat geval niet betrouwbaar.
