Stap 3: Vak → Traject
========================

In deze stap worden de faalkansen van de dijkvakken uit Stap 2 gecombineerd
tot één faalkans voor het traject.

Een dijktraject bestaat uit meerdere dijkvakken en wordt beschouwd als
een seriesysteem: falen van één vak leidt tot falen van het traject.

Bepaling van de trajectfaalkans
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Het lengte-effect is volledig verwerkt op vakniveau via :math:`N_{\mathrm{vak}}`. Daarom worden vakkansen op
trajectniveau **niet opnieuw opgeschaald**.

.. TODO: Wat wordt bedoeld met dit opschalen?

Voor STPH wordt de trajectfaalkans benaderd met:

.. math::

   P_{f,\mathrm{traject}} =
   \sum_{k=1}^{N_{\mathrm{vak}}} P_{f,\mathrm{vak},k}

De bijbehorende betrouwbaarheidsindex volgt uit:

.. math::

   \beta_{\mathrm{traject}} = -\Phi^{-1}(P_{f,\mathrm{traject}})

De α-vector op trajectniveau wordt overgenomen uit het **meest ongunstige vak**.

.. TODO: Doen we dat met de a-vector? En hoe gaat dit op vakniveau? Want dat is niet vermeld in stap 2 volgens mij.
 Wat gaan we verder doen met deze a-vector?

Bepaling van β en α bij assemblage
----------------------------------

Bij het combineren van kansen in GeoProb-Pipe wordt onderscheid gemaakt tussen:

.. TODO: Ik ben toch een beetje in verwarring. We zeggen hierboven ergens hoe we de trajectfaalkans berekenen, en nu
 gaan we onder dit nieuwe kopje opnieuw bespreken hoe we combineren? Het zal vast een reden hebben, maar dit wordt niet
 duidelijk uit de voorgaande tekst (inleiding bijvoorbeeld).

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

.. TODO: De meerwaarde van deze paragraaf (stap 3) wordt niet echt duidelijk. Ik denk dat we nog eens goed moeten
 nadenken welke boodschap we willen overbrengen.