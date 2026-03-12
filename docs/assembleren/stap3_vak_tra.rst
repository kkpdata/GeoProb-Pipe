Stap 3: Vak → traject
========================

In deze stap worden de faalkansen van de dijkvakken uit Stap 2 gecombineerd
tot één faalkans voor het traject.

Een dijktraject bestaat uit meerdere dijkvakken en wordt beschouwd als
een seriesysteem: falen van één vak leidt tot falen van het traject.

Bepaling van de trajectfaalkans
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Het lengte-effect is volledig verwerkt op vakniveau via
:math:`N_{\mathrm{vak}}`.
Daarom worden vakkansen op trajectniveau **niet opnieuw opgeschaald**.

Voor STPH wordt de trajectfaalkans benaderd met:

.. math::

   P_{f,\mathrm{traject}} =
   \sum_{k=1}^{N_{\mathrm{vak}}} P_{f,\mathrm{vak},k}

De bijbehorende betrouwbaarheidsindex volgt uit:

.. math::

   \beta_{\mathrm{traject}} = -\Phi^{-1}(P_{f,\mathrm{traject}})

De α-vector op trajectniveau wordt overgenomen uit het
**meest ongunstige vak**.

Bepaling van β en α bij assemblage
----------------------------------

Bij het combineren van kansen in GeoProb-Pipe wordt onderscheid gemaakt
tussen:

- de **grootte van de faalkans** (:math:`P_f`, β);
- de **richting van falen** (α).

Bij kanscombinaties (scenario → uittredepunt → vak → traject)
wordt de faalkans bepaald via probabilistische aggregatie.

De bijbehorende α-vector wordt steeds overgenomen uit het
**meest ongunstige onderliggende element**, omdat:

- α-vectoren niet lineair optelbaar zijn;
- het falen van het systeem wordt gedomineerd door één kritische
  faalmodus;
- dit consistent is met het seriesysteem-concept.

Concreet betekent dit:

- α\ :sub:`uittredepunt` ← meest ongunstige scenario  
- α\ :sub:`vak` ← meest ongunstige uittredepunt  
- α\ :sub:`traject` ← meest ongunstige vak  