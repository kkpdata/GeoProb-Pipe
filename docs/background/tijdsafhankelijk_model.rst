######################
Tijdsafhankelijk model
######################

Op deze pagina volgt een uitleg van de implementatie van het tijdsafhankelijke model. Achtergronden staan in bijlage 4 van het Technisch rapport Waterspanningen bij Dijken :cite:t:`trw_2004`. 

********************************************
Wanneer is een tijdsafhankelijk model handig
********************************************

In het benedenrivierengebied is de respons van de stijghoogte in het watervoerende zandpakket afhankelijk van zowel de hoogte van het hoogwater als de tijdsduur. Extreme hoogwaterstanden ontstaan door een samenloop van hoge rivierafvoeren, stormopzet op zee en getijdebewegingen.

#uitleg toevoegen vanuit literatuur / bijlage 3?

******************************************************
Tijdsafhankelijk model met een vaste voorlandweerstand
******************************************************

Een dijk op een klei-zand pakket wordt geschematiseerd tot een systeem waarbij er sprake is van verticale elastische consolidatie in de klei, en elastische compactie in het zand (verticale elastische deformatie bij horizontale stroming).

In het technisch rapport waterspanningen bij dijken zijn modellen gegeven die de potentiaal in de zandlaag beschrijven ten gevolge van een sinusvormige hoogwatergolf op de rivier. In de situatie zonder voorland levert dit de volgende modelschematisatie:

.. figure:: /_static/model4d_tijdsafhankelijk_zondervoorland_trwd.png
   :width: 100%

   Schematisering grondwaterstroming tijdsafhankelijk model (figuur b4.11 uit :cite:t:`trw_2004`)


In het geval dat het zandpakket zich relatief stijf gedraagt (geen elastische berging) wordt een verandering van de potentiaal beschreven door:

.. math::

   \phi(x,t)=H_{0} exp(\frac{-0.924 x}{\lambda_{w}^{'}}) cos(\omega t - \frac{0.383 x}{\lambda_{w}^{'}})

De exponentterm levert de amplitudevermindering op locatie :math:`x` van amplitude :math:`H_{0}`. Voor de macrostabiliteit zijn we op zoek naar de maximale respons ten gevolge van een hoogwater. Hierbij verwaarlozen we de faseverschuiving van de respons van de potentiaal in het zandpakket waardoor de formule versimpelt tot:

.. math::
   
   \phi(x)=H_{0} exp(\frac{-0.924 x}{\lambda_{w}^{'}})

Het theoretisch verband tussen de instationaire lekfactor (ook wel cyclische lekfactor) en de stationaire lekfactor :math:`\lambda_{s} = \sqrt{kDc}` is:

.. math::
   
   \lambda_{w}^{'} = \frac{\lambda_{s}}{\sqrt[4]{t_{h}^{'}\omega}}

met :math:`t_{h}^{'} = \frac{d^{2}}{c_{v}^{'}}` in het geval van eenzijdige afstroming.

Dus naast de eigenschappen van het geohydrologische systeem (transmissiviteit zand :math:`kD`, doorlatendheid deklaag :math:`k^{'}` en consolidatiecoëfficiënt van de deklaag :math:`c_{v}^{'}`) is de cyclische lekfactor ook afhankelijk van de duur van de golf via :math:`\omega`. Dit is de hoekfrequentie van de golf:

.. math::
   
   \omega = \frac{2\pi}{T}

met :math:`T` de golfperiode. Voor een getijdebeweging geldt in Nederland een golfperiode van :math:`T =` 12 uur 25 min. Een hoogwatergolf van de rivier heeft een duur van 8 tot 20 dagen (let op golfperiode is 2 maal de duur van een golf). Een stormvloed kent een typische duur van 12 tot 36 uur.

********************************************
Tijdsafhankelijk model met voorlandweerstand
********************************************

Analoog aan het model zonder voorlandweerstand (of met een fictief intredepunt) is ook een model met voorland beschreven. 

.. figure:: /_static/model4d_tijdsafhankelijk_met_voorland_trwd.png
   :width: 100%

   Schematisering grondwaterstroming tijdsafhankelijk model met voorland (figuur b4.12 uit :cite:t:`trw_2004`)


De toplaag in het voorland veroorzaakt een extra weerstand met als gevolg een extra demping van de potentiaalvariaties. Dit levert de volgende formule op:

.. math::

   \phi(x,t) = H_0 exp(\frac{-0.924 x}{\lambda^{´}_{\omega}} - \Delta) cos(\omega t - \frac{0.383}{\lambda^{´}_{\omega}} - \eta)

**************************************
Interpretatie van peilbuiswaarnemingen
**************************************

Door middel van peilbuiswaarnemingen is het mogelijk om zowel de stationaire als de cyclische lekfactor direct te bepalen. Automatisch is daarin de heterogeniteit van de zand- en deklaag verdisconteerd. Uit peilbuiswaarnemingen kunnen niet de aparte eigenschappen worden afgeleid. Een toelichting is gegeven in bijlage 3-6 van het Technisch Rapport Waterspanningen bij dijken.

Uit de peilbuizenwaarnemingen leiden we twee verschillende lekfactoren af:

1. de lekfactoren die het stationaire verloop beschrijven onder gemiddelde rivierwaterstand. en 
2. de lekfactoren die het cyclische (instationaire) verloop beschrijven.

Peilbuiswaarnemingen in het benedenrivierengebied kennen vaak een omvang van meerdere weken of maanden. In deze periode zijn er veel getijdebewegingen, maar ook variaties van een rivierafvoer of mogelijk ook stormopzet. Dit maakt het lastig om eenduidig een peilbuiswaarnemingen te analyseren. De truc is om voor elke getijdebeweging de gemiddelde waarneming en de amplitude te bepalen. Dit doe je voor zowel de rivierwaterstand als de peilbuiswaarnemingen. Op basis van deze afgeleide waarnemingen kies je een of meerdere representatieve getijdebewegingen voor het afleiden van de stationaire en cyclische lekfactoren. Hierbij houd je rekening met de gemiddelde rivierwaterstanden uit de waternormalen en de betrekkingslijnen om een representatieve situatie te vinden. Bij waterkeringen houden we voor gemiddelde omstandigheden een debiet bij Lobith aan van :math:`Q =` 2.200 m<sup>3</sup>/s.

Afleiden van stationaire lekfactoren
====================================

Voor de bepaling van stationaire lekfactor maken we gebruik van de definitie van het kantelpunt:

.. figure:: /_static/Kantelpunt_TRWSD_2004.png
   :width: 100%

   Schematisering kantelpunt (figuur b3.7 uit :cite:t:`trw_2004`)

We kennen de afstanden :math:`x_{i}` van de verschillende peilbuizen :math:`i` tot het kantelpunt. Voor elke peilbuis :math:`i` is de gemiddelde potentiaal :math:`\phi_{i, gem}` bekend. Ook kennen we de gemiddelde rivierwaterstand :math:`\phi_{gem, rivier}`. Onder de aanname van een onverstoorde stijghoogte in de polder :math:`\phi_{p}` kan je per peilbuis de respons :math:`r` uitrekenen door:

.. math::

   r_{i} = \frac{(\phi_{i, gem} - \phi_{p} )}{(\phi_{gem, rivier} - \phi_{p})}

De benedenstroomse randvoorwaarde (de onverstoorde stijghoogte in de polder) kan bijvoorbeeld worden geschat door het polderpeil of regionale grondwaterstromingsmodellen. Het is verstandig om hierin te variëren om het effect daarvan op de berekende stationaire lekfactoren te verkennen.

Het verloop van de respons ten opzichte van het kantelpunt wordt beschreven door:

.. math::

   r(x)= \frac{exp(\frac{-x}{W_{3}})}{(1 + \mu)}

met :math:`\mu = \frac{W_{1}}{W_{3}}`

:math:`W_{1}` staat voor de weerstand in het voorland en :math:`W_{3}` voor die van het achterland. Analoog met het stationaire model van het Technisch Rapport is de weerstand :math:`W` gedefinieerd als:

.. math::

   W = \lambda tanh(\frac{L}{\lambda})

Geometrische factoren worden dus impliciet meegenomen. Twee peilbuizen op korte afstand tot het kantelpunt (de dijk) zijn vaak voldoende om een inschatting te krijgen van de weerstand van het voorland en achterland.

Afleiden van instationaire lekfactoren
======================================

We kennen de afstanden :math:`x_{i}` van de verschillende peilbuizen :math:`i` tot het kantelpunt (de dijk). Per getijdebeweging is voor elke peilbuis :math:`i` de amplitude bekend. Ook kennen we per getijdebeweging de amplitude van de getijdebeweging op de rivier. Op deze manier is het mogelijk om een extrapolatie uit te voeren volgens de hoogste standen, zoals in onderstaande figuur is weergegeven.

.. figure:: /_static/TheoretischeVerbandCyclischePeilbuiswaarnemingen_TRWSD_2004.png
   :width: 100%

   Theoretisch verband Cylische lekfactoren (figuur b3.9 uit :cite:t:`trw_2004`)

We willen echter een extrapolatie uitvoeren volgens tijdsafhankelijke methode. Uit de figuur volgt dat met deze methode een iets lagere respons te vinden is dan een fit bij de hoogste waterstanden. Hiervoor is het noodzakelijk om een ellips te fitten op de waarnemingen. Vanwege uitloop en inschakeleffecten kiezen we voor de fit een dataset met waarnemingen 3 uur voor en 3 uur na de top, zie punt 2 in onderstaande figuur.

.. figure:: /_static/SchematischeHoogwaterRespons_TRWSD_2004.png
   :width: 100%

   Inschakel en uitloopeffect (figuur b3.11 uit :cite:t:`trw_2004`)

Uit de fit volgen diverse parameters. Voor het afleiden van de instationaire lekfactoren is de respons het belangrijkst, weergegeven door de hoek :math:`\theta`. De respons van de amplitude op de rivier en dus ook de hoek :math:`\theta` neemt af richting het achterland.

Gegeven de afgeleide amplitudes hebben we zowel een fit uitgevoerd met met model met en zonder voorlandweerstand. Hieruit bleek een fit met het model met voorlandweerstand onrealistische waarden op te leveren voor de voorlandweerstand. De reden hiervoor is dat de de rivierbodem van de Lek een grote weerstand kent waardoor de amplitudes van de getijdebeweging in het achterland sterk gedempt zijn. Ook kan de implementatie in python niet 100% kloppen.

Het model zonder voorlandweerstand wordt in de ontwerppraktijk veel gebruikt omdat we bij het definiëren van een fictief intredepunt veel controle hebben over de schematisatie. Het nadeel van deze methode is dat bij superpositie naar een hoogwater het de respons overschat omdat de voorlandweerstand (via het fictieve intredepunt) niet schaalt met de langere duur van de stormopzet en rivierafvoer.

De (aangepaste) formule die gebruikt is om een fit uit te voeren is:

.. math::

   \phi(x)=H_{0} exp(\frac{-0.924 (x + x_{intrede})}{\lambda_{w}^{'}})



Gemiddeld potentiaalverloop
---------------------------

De waterstand en de respons worden gegeven ten opzichte van de gemiddelde waterstand, respectievelijk grondwaterpotentiaal. De implementatie maakt gebruik van het principe van het kantelpunt.

.. math::

   \phi(x) = h_{ref} + r(x) (h_{rivier} - h_{ref})

   r(x) = \frac{exp(\frac{- x_{tp}}{W_{3}})}{1+\frac{W_1}{W_3}}

Superpositie
============

Door middel van bovenstaande fit is het mogelijk om de respons op de getijdebeweging van de rivier te beschrijven als functie van de afstand :math:`x` tot het kantelpunt ten opzichte van een verondersteld gemiddeld potentiaalverloop. Voor een extrapolatie naar WBN zijn ook de bijdragen van de stormopzet en de rivierafvoer nodig. Hiervoor gebruiken we het principe van superpositie. Uitgaande van constante eigenschappen van het geohydrologische systeem zijn cyclische lekfactoren bij andere perioden dan de getijdebeweging af te leiden door: 

.. math::

   \lambda_{\omega, T_{2}}^{'} = \lambda_{\omega, T_{1}}^{'} \sqrt[4]{\frac{T_{2}}{T_{1}}}

Waarin het supscript :math:`T_{1}` staat voor de periode van de getijdebeweging. De instationaire lekfactor bij andere periode :math:`T_{2}` schaalt dus met een 4e machts wortel.

We kennen nu de lekfactoren bij andere belastingsperiodes. Om de respons op een extreem hoogwater op de rivier te berekenen, moeten we de bijdrage (amplitudes) van de getijdebeweging, de stormopzet en de rivierafvoer kennen. De topwaterstand van de rivier :math:`\phi_{rivier}` bij een gegeven terugkeertijd :math:`T` beschrijven we door:

.. math::

   \phi_{rivier} (T) = \phi_{gem, rivier} + A_{rivier} (T) + A_{storm}(T) + A_{getijde} (T)


Omgang met onzekerheden gegeven de terugkeertijd
================================================

Voor piping en macrostabiliteitsberekeningen moeten we het potentiaalverloop in de zandlaag kennen, gegeven de topwaterstand bij een terugkeertijd. Dit potentiaalverloop is onzeker en zowel afhankelijk van onzekerheden in de belastingen als de respons van het geohydrologische systeem.

Onzekerheden in de belastingen zijn:

* stormduur
* stormopzet
* duur van de afvoergolf
* rivierafvoer
* getijdebeweging

De respons van het geohydrologische systeem wordt beschreven door :math:`\lambda_{\omega}^{'}` afhankelijk van de duur (periode) van de verschillende componenten van de belasting: opzet door rivierafvoer, stormopzet en de getijdebeweging. De voorlandweerstand is opgenomen in de intredelengte :math:`x_{intrede}`. De onzekerheden worden beschreven door een variatiecoëfficiënt op de verwachtingswaarde.

Uit de formule van de superpositie volgt dat kleine onzekerheden in de duur van een component weinig invloed hebben op de respons. Voor de respons is het belangrijk om te 
#todo: verder uitwerken.
Omdat de belangrijkste componenten (storm en rivierafvoer) via de tijdsduur een beperkte invloed hebben op de respons van het geohydrologische systeem, is er voor gekozen deze als determinist te kiezen en deze onzekerheid in de verdeling van de lekfactor op te nemen. 


Verdeling van de bijdrage van de componenten aan de topwaterstand
=================================================================

Een topwaterstand bij terugkeertijd :math:`T` ontstaat door een combinatie van hoge rivierafvoeren, stormopzet op zee en het getij. Afhankelijk van de locatie in het benedenrivierengebied hebben rivierafvoeren of stormopzet meer invloed. De beschikbare waterstandsstatistiek geeft voor relevante topwaterstanden (:math:`T > 10` jaar) een percentielverdeling van de afvoer bij Lobith. Deze verdeling verschilt per terugkeertijd. Op basis van deze percentielen is een verdeling afgeleid, gegeven de terugkeertijd :math:`T`.

Ook de amplitude van het getij :math:`A_{getij}` is afhankelijk van de rivierafvoer als een hoogwater optreedt. Als een hoge waterstand optreedt in het geval van hoge rivierafvoeren, is de stroomsnelheid zodanig dat de amplitude van het getij sterk afneemt. In eerdere studies van het waterstandsverloop is afgeleid/aangenomen dat bij een debiet :math:`Q = 14.000 m^{3}/s` bij Lobith de getijdeslag bijna geheel is gedempt.

Voor deze studie beschrijven de amplitude van het getij als functie van het debiet, dus :math:`A_{getij}(Q)`.

Ook de amplitude van de rivier is voor de locatie in het benedenrivierengebied benaderd door een formule. Beschikbare betrekkingslijnen geven per rivierkilometer de waterstand gegeven het debiet bij Lobith. Omdat we de gemiddelde rivierwaterstand :math:`\phi_{gem, rivier}` ook hebben afgeleid kunnen we voor elk debiet boven de gemiddelde rivierwaterstand met de betrekkingslijnen een amplitude uitrekenen.

Voor een topwaterstand en een gegeven debiet :math:`Q` zijn nu de amplitudes van het getij :math:`A_{getij}(Q)` en de rivierafvoer :math:`A_{rivier}(Q)` bekend en kan de stormopzet ook worden uitgerekend. Merk op dat de modelonzekerheid van de waterstand hierdoor automatisch bij de stormopzet terecht komt, en niet verdeeld wordt bij over de rivierafvoer en getijdebeweging.

Het model is vanuit praktische overwegingen geïmplementeerd in de probabilistische toolkit. Ook de overige onzekerheden van belasting en sterkte zijn hierin gedefinieerd. Via monte carlo analyse zijn trekkingen gegenereerd. Voor elke realisatie is vervolgens de respons van de potentiaal in het watervoerende zandpakket uitgerekend. Dit levert per :math:`x` een verdeling op van de potentiaal in het watervoerende zandpakket. 

.. bibliography