Truncated verdelingen
=====================

In probabilistische berekeningen kunnen stochasten waarden aannemen die vanuit
statistisch oogpunt mogelijk zijn, maar fysisch niet realistisch of zelfs
onmogelijk. Dit komt met name voor bij normaal verdeelde variabelen, waarvan
het theoretische domein onbegrensd is.

Om te voorkomen dat dergelijke fysisch onmogelijke waarden worden gebruikt in
de betrouwbaarheidsanalyse, kunnen stochasten worden begrensd door toepassing
van een *truncated distribution*. Hierbij wordt een ondergrens (*minimum*) en
een bovengrens (*maximum*) opgegeven. De kansmassa buiten deze grenzen wordt
verwijderd en de overblijvende verdeling wordt opnieuw genormaliseerd. Hierdoor
kunnen geen waarden meer worden getrokken buiten het fysisch plausibele bereik.

Het toepassen van truncatie heeft twee voordelen:

* Het voorkomt fysisch onmogelijke invoerwaarden tijdens de analyse.
* Het kan leiden tot een realistischer ontwerp- en faalmechanisme wanneer het design point wordt gedomineerd door extreme waarden die in de praktijk niet kunnen voorkomen.

Gebruik van truncatie
---------------------

GeoPob-Pipe hanteert standaard grenzen voor een aantal veelgebruikte stochasten.
Deze grenzen zijn gebaseerd op praktische fysische aannames en dienen als
eerste controle tegen onrealistische waarden.

Tijdens een betrouwbaarheidsanalyse wordt aanbevolen om het design point te
controleren. Wanneer blijkt dat één of meerdere stochasten in het design point
waarden aannemen die fysisch niet plausibel zijn, kunnen de truncatiegrenzen
worden aangescherpt. Hierdoor wordt de berekening beter afgestemd op het
daadwerkelijke fysische gedrag van het systeem.

De standaardwaarden vormen daarom geen vaste voorschriften, maar een hulpmiddel
om onrealistische modeluitkomsten te voorkomen.



