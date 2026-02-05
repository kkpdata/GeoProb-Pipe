.. _assembleren:

.. contents::
   :local:
   :depth: 3


Assembleren
===========

Doel en scope
-------------

Deze pagina beschrijft de assemblage van faalkansen binnen `GeoProb-Pipe`
voor het faalmechanisme STPH (piping).
De assemblage combineert lokaal berekende faalkansen op uittredepuntniveau
tot faalkansen op vak- en trajectniveau.

Bron en afbakening
------------------

De assemblage van faalkansen in GeoProb-Pipe is conceptueel gebaseerd op
de bottom-up assemblage zoals beschreven door het Adviesteam Dijkontwerp
in :cite:`ADO2024Assembleren`.

In deze publicatie wordt de assemblage beschreven vanuit een klassieke
opzet, waarbij faalkansen op doorsnedeniveau worden opgeschaald naar
vak- en trajectniveau.

GeoProb-Pipe volgt dezelfde **systemische principes** (seriesysteem,
lengte-effect, SOM/MAX), maar hanteert een **andere elementaire
bouwsteen**:

*De assemblage start niet bij een doorsnede, maar bij een uittredepunt,
waarin meerdere deelfaalmechanismen van STPH en ondergrondscenario’s
probabilistisch worden gecombineerd.*

Hierdoor wijkt met name de eerste stap van de assemblage inhoudelijk af
van Rode draad #10, terwijl de vervolgstappen hiermee consistent blijven.

Conceptuele opbouw (hiërarchie)
-------------------------------

.. figure:: _static/Hierarchie_berekeningen.png
   :width: 95%
   :align: center

   Hiërarchische opbouw van faalkansen in GeoProb-Pipe van uittredepunt
   tot trajectniveau.

Stap 1: Scenario → uittredepunt
-------------------------------

In GeoProb-Pipe vormt het **uittredepunt** de kleinste zelfstandige
bouwsteen in de assemblage van faalkansen.
Een uittredepunt representeert een fysieke locatie langs de waterkering
waar piping kan initiëren.

In tegenstelling tot de klassieke BOI-benadering wordt geen enkele
doorsnede beschouwd, maar een **hiërarchische combinatie van
faalmechanismen en scenario’s**.

Faalmechanismen en scenario’s
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Per uittredepunt worden meerdere faalmechanismen beschouwd, waaronder:

- uplift
- heave
- piping

Voor elk faalmechanisme worden meerdere hydraulische en geotechnische
scenario’s doorgerekend.
Per scenario wordt een faalkans bepaald, inclusief bijbehorende
FORM-resultaten (β en α).

De faalkans per scenario wordt bepaald met Importance Sampling rondom
de FORM-design points.

Combinatie tot faalkans per uittredepunt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

De faalkans van een uittredepunt volgt uit de combinatie van alle
scenario’s die tot falen kunnen leiden:

.. math::

   P_{f,\mathrm{uittrede}} =
   \sum_{i=1}^{N_\mathrm{scen}}
   P(\mathrm{scenario}_i)\, P_f(\mathrm{scenario}_i)

De bijbehorende betrouwbaarheidsindex volgt uit:

.. math::

   \beta_{\mathrm{uittrede}} = -\Phi^{-1}(P_{f,\mathrm{uittrede}})

De richting van falen (α-vector) wordt **niet gemiddeld**, maar
overgenomen uit het **meest ongunstige scenario**, omdat dit scenario
dominant is voor het optreden van falen.

Stap 2: Uittredepunt → vak
--------------------------

Een dijkvak bevat meerdere uittredepunten waar piping kan initiëren.
De faalkans per vak volgt uit het combineren van deze bijdragen,
rekening houdend met het lengte-effect.

.. _fig-bottom-up-traject:

.. figure:: _static/bottom-up.png
   :alt: Bottom-up assemblage van traject naar vakniveau met SOM/MAX en lengte-effect.
   :align: center
   :width: 95%

   Schematische weergave van bottom-up assembleren van traject naar
   vakniveau. De trajectfaalkans wordt opgebouwd uit vakkansen (SOM/MAX),
   waarbij op vakniveau het lengte-effect wordt gemodelleerd via
   :math:`N_{\mathrm{vak}}`.

:numref:`fig-bottom-up-traject` laat zien hoe faalkansen op hoger schaalniveau
worden opgebouwd uit onderliggende elementen en waar het lengte-effect
in de assemblage wordt toegepast.

Lengte-effect en opschaling
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Het aantal effectieve, onafhankelijke bijdragen binnen een vak wordt
benaderd met:

.. math::

   N_{\mathrm{vak}} =
   \max\left(
       1,\;
       a_{\mathrm{vak}} \frac{L_{\mathrm{vak}}}{\Delta L}
   \right)

waarbij:

- :math:`L_{\mathrm{vak}}` de lengte van het vak is;
- :math:`\Delta L` de equivalente onafhankelijke lengte voor STPH;
- :math:`a_{\mathrm{vak}}` de mechanismegevoelige fractie van het vak.

Bepaling van de faalkans per vak
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

De faalkans van het vak wordt bepaald met:

.. math::

   P_{f,\mathrm{vak}} =
   N_{\mathrm{vak}} \cdot P_{f,\mathrm{uittrede,rep}}

Hierin is :math:`P_{f,\mathrm{uittrede,rep}}` de representatieve
faalkans per uittredepunt binnen het vak.

De ondergrens van de vakkans wordt bepaald door de grootste individuele
uittredepuntfaalkans; de bovengrens volgt uit de SOM-benadering.

In een vervolgstap kan :math:`P_{f,\mathrm{uittrede,rep}}` worden
afgeleid uit DSN-resultaten, bijvoorbeeld via een moving window-
benadering of via een representatieve discretisatie gekoppeld aan
:math:`\Delta L`.

Stap 3: Vak → traject
----------------------

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

Samenvatting
------------

De assemblage van faalkansen voor STPH in GeoProb-Pipe verloopt
bottom-up, van scenario via uittredepunt en vak naar traject.
Het lengte-effect wordt uitsluitend toegepast bij de overgang van
uittredepunt naar vak, waarmee dubbeltelling wordt voorkomen.

Deze werkwijze resulteert in een consistente, transparante en
fysisch onderbouwde bepaling van de trajectfaalkans voor piping.

