Kader
=====

De assemblage van faalkansen in GeoProb-Pipe is conceptueel gebaseerd op de bottom-up assemblage zoals beschreven door
het Adviesteam Dijkontwerp in Rode Draad #10 :cite:`ADO2024Assembleren`. In deze publicatie wordt de assemblage
beschreven vanuit een klassieke opzet, waarbij faalkansen op doorsnedeniveau worden opgeschaald naar vak- en
trajectniveau.

GeoProb-Pipe volgt dezelfde **systemische principes** (seriesysteem, lengte-effect, SOM/MAX), maar hanteert een
**andere elementaire bouwsteen**:

    *De assemblage start niet bij een doorsnede, maar bij een uittredepunt,
    waarin meerdere deelfaalmechanismen van STPH en ondergrondscenario’s
    probabilistisch zijn gecombineerd.*

Hierdoor wijkt met name de eerste stap van de assemblage inhoudelijk af van Rode Draad #10, terwijl de verdere
opschaling naar trajectniveau conceptueel consistent blijft.

De faalkans van een traject wordt opgevat als een seriesysteem van uittredepunten: falen treedt op zodra één van de
uittredepunten faalt. De werkelijke trajectkans wordt daarbij bepaald door de onderlinge afhankelijkheid tussen
uittredepunten. Deze afhankelijkheid is in de praktijk niet exact bekend en vormt de belangrijkste onzekerheid in de
assemblage.

Het lengte-effect wordt gebruikt als een model om deze ruimtelijke afhankelijkheid te benaderen. Afhankelijk van de
gekozen methode wordt dit effect expliciet of impliciet meegenomen.


.. todo::

    Onderstaande warning oplossen.


.. warning::

    Hierboven wordt `gekozen methode` geïntroduceerd. In de volgende alinea wordt een methode genoemd. Maar de methodes
    worden helemaal niet geïntroduceerd. Daarmee blijft in het ongewis welke methodes er zijn en valt de Window-methode
    ineens uit het niets.


De Window-methode is gebaseerd op de benadering zoals beschreven in `Probabilistische analyses en combinatie
pipinganalyses uittredepuntenmethode` :cite:`DEL2021`. In deze studie worden uittredepuntresultaten binnen vaste
vensters gecombineerd om het lengte-effect te benaderen, waarbij afhankelijkheid binnen vensters volledig wordt
verondersteld en tussen vensters wordt genegeerd.

Om met deze onzekerheden om te gaan, zijn binnen GeoProb-Pipe meerdere methoden geïmplementeerd om de trajectkans te
benaderen.