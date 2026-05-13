Faalkans uittredepuntniveau
===========================

In GeoProb-Pipe vormt het **uittredepunt** de kleinste zelfstandige bouwsteen in de assemblage van faalkansen. Een
uittredepunt is een fysieke locatie langs de waterkering waar piping kan initiëren. In tegenstelling tot de klassieke
BOI-benadering wordt geen doorsnede beschouwd, maar een reeks uittredepuntlocaties langs het traject. Per uittredepunt
worden meerdere **ondergrondscenario’s** doorgerekend, zie voorgaande pagina ':doc:`stap0_sc`'.

Van scenarioberekening naar de betrouwbaarheid van het uittredepunt
-------------------------------------------------------------------

De resultaten uit de scenarioberekeningen worden samengevoegd tot één faalkans per uittredepunt door de individuele
scenariokansen als wegingsfactor te gebruiken.

Indien één van de scenarioberekeningen niet convergeert, wordt het betreffende uittredepunt als niet geconvergeerd
beschouwd. De verdere opschaling naar vak- en trajectniveau (zie documentatie in volgende pagina's) zal dan ook als
niet geconvergeerd worden beschouwd.
