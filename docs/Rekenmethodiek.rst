.. _rekenmethodiek:

Rekenmethodiek
==============

Berekeningsmodellen
-------------------

In de schematiseringshandleiding piping :cite:`sh_piping_2021` zijn de berekeningsmodellen beschreven die gebruikt worden in het BOI.
Piping treedt op wanneer de deklaag opbarst, heave optreedt en er doorgaande terugschrijdende erosie plaatsvindt.

TODO: foutenboom toevoegen als plaatje?

De grenstoestandfunctie van **opbarsten** :math:`Z_{u}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{u} = m_{u} \cdot \Delta \phi_{c,u} - (\phi_{exit} - h_{exit})

waarbij :math:`m_{u}` de modelfactor voor opbarsten is [-]. 
De grenspotentiaal ten opzichte van maaiveldniveau :math:`\Delta \phi_{c,u}` [m] wordt bepaald door het effectieve gewicht van de deklaag onder water:

.. math::

   \Delta \phi_{c,u} = \frac{d_{deklaag} \cdot (\gamma_{sat,deklaag} - \gamma_{w})}{\gamma_{w}}

waarin:

- :math:`d_{deklaag}` de dikte van de deklaag is [m]
- :math:`\gamma_{sat}` het gemiddeld verzadigd volumegewicht van de cohesieve deklaag is [kN/m³]
- :math:`\gamma_{w}` het volumegewicht van water is [kN/m³]

De dikte van de deklaag :math:`d_{deklaag}` ter plaatse van het uittredepunt is definieerd als de verticale afstand tussen het maaiveldniveau en de bovenkant van de pipinggevoelige zandlaag:

.. math::

   d_{deklaag} = mv_{exit} - top_{zandlaag}

waarin:
- :math:`mv_{exit}` maaiveldniveau ter plaatse van uittredepunt [m+NAP]
- :math:`top_{zandlaag}` niveau bovenkant van de pipinggevoelige zandlaag [m+NAP]

De stijghoogte ter plaatse van het uittredepunt :math:`\phi_{exit}` [m+NAP] wordt volgens de schematiseringshandleiding :cite:`sh_piping_2021` beschreven door:

.. math::

   \phi_{exit} = \phi_{polder} + r_{exit} \cdot (h_{rivier} - \phi_{polder})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]
- :math:`r_{exit}` de dempingsfactor ter plaatse van het uittredepunt [-]
- :math:`h_{rivier}` het waterniveau in de rivier [m+NAP]

De dempingsfactor :math:`r_{exit}` ter plaatse van het uittredepunt is afhankelijk van de locatie van het uittredepunt ten opzichte van de dijk en de geohydrologische situatie. De schematiseringshandleiding piping :cite:`sh_piping_2021` hanteert dit als een onafhankelijke invoerparameter.


:math:`h_{exit}` is de randvoorwaarde in het uittrredepunt gedefinieerd door het maximumm van het polderpeil en het maaiveldniveau ter plaatse van het uittredepunt:

.. math::

   h_{exit} = max(\phi_{polder} + mv_{exit})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]


De grenstoestandfunctie van **heave** :math:`Z_{h}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{h} = m_{h} \cdot i_{i,c} - \frac{\phi_{exit} - h_{exit}}{d_{deklaag}}

waarin:

- :math:`m_{h}` de modelfactor voor heave is [-]
- :math:`i_{i,c}` de kritieke heave gradiënt is [-]

Opgemerkt wordt dat de modelfactoren :math:`m_{u}` en :math:`m_{h}` niet zijn opgenomen in de formules van de schematiseringshandleiding piping :cite:`sh_piping_2021`, maar wel in deze implementatie zijn opgenomen om de modelonzekerheid expliciet te kunnen kwantificeren.

De grenstoestandfunctie van **terugschrijdende erosie** :math:`Z_{p}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{p} = m_{p} \cdot \Delta H_{c} - \Delta h_{red}

met :math:`\Delta h_{red}` het gereduceerde verval over de deklaag [m] als:

.. math::
   
   \Delta h_{red} = h_{buitenwaterstand} - h_{exit} - r_{c,deklaag} \cdot d_{deklaag}

waarin:

- :math:`m_{p}` de modelfactor voor terugschrijdende erosie is [-]
- :math:`\Delta H_{c}` het kritieke verval over de deklaag is [m]
- :math:`h_{buitenwaterstand}` de buitenwaterstand is [m+NAP]
- :math:`h_{exit}` de randvoorwaarde in het uittredepunt is [m+NAP]
- :math:`r_{c,deklaag}` de reductieconstante van het verval over de deklaag is [-]
- :math:`d_{deklaag}` de dikte van de deklaag is [m]

 Het kritieke verval over de deklaag :math:`\Delta H_{c}` is gebaseerd op het in 2011 aangepaste model van Sellmeijer.

 .. math::

   \Delta H_{c} = L_{kwelweg} \cdot F_{resistance} \cdot F_{scale} \cdot F_{geometry}

met:

.. math::

   F_{resistance} = \eta \frac{\gamma_{korrel} - \gamma_{w}}{\gamma_{w}} \cdot tan(\theta)

   F_{scale} = \frac{d_{70,m}}{\sqrt[3]{L_{kwelweg} \cdot \frac{k \cdot \upsilon_{w}}{g}}} \left(\frac{d_{70}}{d_{70,m}} \right)^{0.4}

   F_{geometry} = 0.91 \left(\frac{D_{wvp}}{L_{kwelweg}} \right)^{\frac{0.28}{\left(\frac{D_{wvp}}{L_{kwelweg}} \right)^{2.8} - 1} + 0.04}


waarin:

- :math:`L_{kwelweg}` de kwelweglengte is [m]. Deze is gedefinieerd als de horizontale afstand tussen het uittredepunt en een onzeker intredepunt.
- :math:`\eta` coëfficiënt van White (sleepkrachtfactor) [-]. Standaardwaarde is 0.25
- :math:`\gamma_{korrel}` Volumieke dichtheid zand [kN/m³]. Standaardwaarde is 26.0 kN/m³
- :math:`\gamma_{w}` het volumegewicht van water is [kN/m³]
- :math:`\theta` de rolweerstandshoek van zandkorrels van de aangepaste Sellmeijer rekenregel is [°]. Standaardwaarde is 37°
- :math:`d_{70,m}` de referentie :math:`d_{70}` waarde is [m]. Standaardwaarde is 2.08E-4 m
- :math:`d_{70}` de 70-percentielwaarde van de korrelverdeling van de pipinggevoelige laag is [m]
- :math:`k` de darcy doorlatendheid van de zandlaag is [m/s]
- :math:`\upsilon_{w}` de kinematische viscositeit van water is [m²/s]. Standaardwaarde is 1.33E-6 m²/s bij 10°C
- :math:`g` de zwaartekrachtversnelling is [m/s²]. Standaardwaarde is 9.81 m/s²
- :math:`D_{wvp}` de dikte van de watervoerende zandlaag is [m]


Berekeningsmodel met stijghoogtemodel 4a
----------------------------------------

De drijvende kracht achter terugschrijdende erosie is grondwaterstroming. Door het analytische grondwatermodel 4a van :cite:`trw_2004` toe te passen, kan de respons :math:`r_{exit}` in het uittredepunt beschreven worden als functie van de locatie in het dwarspofiel :math:`x_{exit}` [m] en de geohydrologische parameters van model 4a. Uitleg over het model 4a is te vinden in de :ref:`stationair-model`. De repons in het uittredepunt wordt dan:

.. math::

   r_{exit}(x) = f(x_{exit}, L_1, L_2, L_3, c_{voorland}, c_{achterland}, k, D_{wvp})

Geometrische parameters :math:`L_1` en :math:`L_2` zijn omgeschreven naar afstanden ten opzichte van het uittredepunt:

.. math::

   L_1 = L_{intrede} - L_{but}

   L_2 = L_{but} - L_{bit}

waarin:

- :math:`L_{intrede}` de afstand van het uittredepunt tot een geometrische intredelijn [m]
- :math:`L_{but}` de afstand van het uittredepunt tot de buitenteen [m]
- :math:`L_{bit}` de afstand van het uittredepunt tot de binnenteen [m]
- :math:`L_3` de achterlandlengte [m]
- :math:`x_{exit}` de afstand van het uittredepunt tot de binnenteen [m]. De aanname is dat uittredepunten altijd binnendijks van een (denkbeeldige) binnenteen liggen.
- :math:`c_{voorland}` de weerstand van de deklaag in het voorland [dag]
- :math:`c_{achterland}` dde weerstand van de deklaag in het achterland [dag]

De kwelweglengte :math:`L_{kwelweg}` maakt conform de schematiseringshandleiding piping :cite:`sh_piping_2021` gebruik van het principe van de effectieve voorlandlengte. 

.. math::

   L_{kwelweg} = L_{but} + L_{eff,voorland}

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   \lambda_{1} = \sqrt{c_{voorland} \cdot k \cdot D_{wvp}}

waarin:

- :math:`L_{eff,voorland}` de effectieve voorlandlengte is [m]
- :math:`\lambda_{1}` de spreidingslengte van het voorland is [m]

Overzicht parameters berekeningsmodel met model 4a
--------------------------------------------------

Het berekeningsmodel met het analytische grondwatermodel 4a kent de volgende invoerparameters:

.. list-table:: Invoerparameters berekeningsmodel met model 4a
   :widths: 20 60 20 
   :header-rows: 1

   * - Variable
     - Omschrijving
     - Verdeling/Constante
   * - :math:`h_{buitenwaterstand}`
     - Buitenwaterstand [m+NAP]
     - CDF
   * - :math:`\phi_{polder}`
     - Waterniveau in de polder [m+NAP]
     - deterministisch
   * - :math:`mv_{exit}`
     - Maaiveldniveau ter plaatse van uittredepunt [m+NAP]
     - deterministisch
   * - :math:`r_{c,deklaag}`
     - Reductieconstante van het verval over de deklaag [-]
     - lognormaal
   * - :math:`L_{bit}`
     - Afstand van het uittredepunt tot de binnenteen [m]
     - deterministisch
   * - :math:`L_{but}`
     - Afstand van het uittredepunt tot de buitenteen [m]
     - deterministisch
   * - :math:`L_{intrede}`
     - Afstand van het uittredepunt tot geometrische intredelijn [m]
     - deterministisch
   * - :math:`L_{3}`
     - Achterlandlengte [m]
     - deterministisch
   * - :math:`top_{zandlaag}`
     - niveau bovenkant van de pipinggevoelige zandlaag [m+NAP]
     - normaal
   * - :math:`c_{voorland}`
     - Weerstand van de deklaag in het voorland [dag]
     - lognormaal
   * - :math:`c_{achterland}`
     - Weerstand van de deklaag in het achterland [dag]
     - lognormaal
   * - :math:`D_{wvp}`
     - Dikte van de watervoerende zandlaag [m]
     - lognormaal
   * - :math:`kD_{wvp}`
     - Transmissiviteit van het watervoerende pakket [m²/dag]
     - lognormaal
   * - :math:`d_{70}`
     - 70-percentielwaarde van de korrelverdeling van de pipinggevoelige laag [m]
     - lognormaal
   * - :math:`\gamma_{sat,deklaag}`
     - Gemiddeld verzadigd volumegewicht deklaag [kN/m³]
     - lognormaal, shift = 10.0
   * - :math:`i_{i,c}`
     - Kritieke heave gradiënt [-]
     - lognormaal
   * - :math:`d_{70,m}`
     - Referentiewaarde voor de :math:`d_{70}` [m]
     - 2.08E-4 m
   * - :math:`\upsilon_{w}`
     - Kinematische viscositeit van water [m²/s]
     - 1.33E-6 m²/s bij 10°C
   * - :math:`\eta`
     - Coëfficiënt van White (sleepkrachtfactor) [-]
     - 0.25
   * - :math:`\theta`
     - Rolweerstandshoek van zandkorrels van de aangepaste Sellmeijer rekenregel [°]
     - 37°    
   * - :math:`g`
     - Zwaartekrachtversnelling [m/s²]
     - 9.81 m/s²
   * - :math:`\gamma_{korrel}`
     - Volumieke dichtheid zand [kN/m³]
     - 26.0 kN/m³
   * - :math:`\gamma_{w}`
     - Volumegewicht van water [kN/m³]
     - 9.81 kN/m³
   * - :math:`m_{u}`
     - Modelfactor opbarsten [-]
     - normaal
   * - :math:`m_{h}`
     - Modelfactor heave [-]
     - normaal
   * - :math:`m_{p}`
     - Modelfactor terugschrijdende erosie [-]
     - normaal

Berekeningsmodel met andere (numerieke) stijghoogtemodellen
-----------------------------------------------------------

In plaats van het analytische grondwatermodel 4a kan ook een ander (numeriek) stijghoogtemodel worden gebruikt om de respons in het uittredepunt te bepalen. In het geval van Waterschap Rivierenland is dat het regionale grondwaterstromingsmodel MORIA. Informatie van numerieke modellen is vaak beschikbaar in de vorm van een grid. Per uittredepunt kunnen de geohydrologische parameters worden uitgelezen uit het grid. De benodigde variabelen zijn:

- :math:`\phi_{gemiddeld}(x,y)` een grid met het gemiddelde grondwaterstandniveau bij gemiddelde rivierwaterstand [m+NAP]
- :math:`h_{gemiddeld}` de gemiddelde rivierwaterstand nabij het uittredepunt [m+NAP]
- :math:`r_{exit}(x,y)` een grid met de respons in het uittredepunt [-]
- :math:`\lambda_{1}` de spreidingslengte van het voorland [m]

De stijghoote in het uittredepunt wordt dan:

.. math::

   \phi_{exit}(x,y) = \phi_{gemiddeld}(x,y) + m_{gw} \cdot r_{exit}(x,y) \cdot (h_{buitenwaterstand} - h_{gemiddeld})

   L_{eff,voorland} = \lambda_{1} \cdot tanh(\frac{L_1}{\lambda_{1}})

   L_{kwelweg} = L_{but} + L_{eff,voorland}

waarin :math:`m_{gw}` de modelfactor voor het stijghoogtemodel is [-].

De beschrijving van het geohydrologische systeem met deze variabelen betekent ook dat de onderlinge correlatie van de variabelen apart moet worden gedefinieerd. Dit betreft met name de correlatie tussen de spreidingslengte van het voorland :math:`\lambda_{1}` en de transmissiviteit van het watervoerende zandpakket :math:`kD` en in mindere mate de correlatie tussen de respons in het uittredepunt :math:`r_{exit}` en de transmissiviteit van het watervoerende zandpakket :math:`kD`. In het model 4a zijn deze correlaties modelmatig beschreven.


