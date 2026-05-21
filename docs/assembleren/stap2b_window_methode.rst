Window-methode
==============

De Window-methode deelt een dijktraject in vakken met een vooraf gedefinieerde grootte. De grootte van het window (de
vak) bepaalt de mate van lengte-effect.

De trajectkans wordt benaderd door de volgende uitgangspunten:

1. Voor alle berekende uittredepunten is de ligging bekend. Binnen de window wordt de maximale faalkans van alle
uittredepunten in de window als vakkans genomen. Dit veronderstelt volledige afhankelijkheid binnen een window.
2. Tussen windows is er geen afhankelijkheid. De onafhankelijke verzameling windows (vakken) bepaalt de trajectkans.

De lengte van het window is dus een maat voor het lengte-effect en kan worden vergeleken met de equivalente 
onafhankelijke lengte :math:`ΔL`. 
De mate van lengte-effect is op voorhand niet bekend. Daarom bepaalt GeoProb-Pipe voor verschillende windowsgroottes 
de systeemkans.