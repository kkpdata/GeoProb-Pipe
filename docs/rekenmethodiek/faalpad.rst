Faalpad en foutenboom piping
============================

In :numref:`faalpad-STPH` zie je een veelvoorkomend faalpad voor het faalmechanisme *piping* :cite:`HOVK_STPH_2024`.
`GeoProb-Pipe` richt zich op het modelleren van de initiële mechanismen die leiden tot piping: opbarsten, heave en
terugschrijdende erosie. Hierbij wordt aangenomen dat piping optreedt wanneer de deklaag opbarst, heave optreedt en
er doorgaande terugschrijdende erosie plaatsvindt. In de schematiseringshandleiding piping :cite:`sh_piping_2021`
zijn de bijbehorende grenstoestandsfuncties beschreven die in het BOI en in `GeoProb-Pipe` worden gebruikt.

.. _faalpad-STPH:

.. figure:: _static/faalpad_piping.png
   :alt: Veelvoorkomend faalpad voor het faalmechanisme piping.
   :align: center

   Veelvoorkomend faalpad voor het faalmechanisme *piping* :cite:`HOVK_STPH_2024`.

.. TODO: Foutenboom toevoegen als plaatje?

Basis grenstoestandsfuncties BOI
--------------------------------

De onderstaande grenstoestandsfuncties vormen de kern van de berekening in `GeoProb-Pipe`.
Ze worden identiek toegepast in elk stijghoogtemodel (`limit_state_wbi`, `limit_state_model4a`, `limit_state_moria`).
De verschillen tussen de modellen zitten uitsluitend in de berekening van de stijghoogte :math:`\phi_{exit}` en bijbehorende parameters.

Opbarsten
~~~~~~~~~

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

De dikte van de deklaag :math:`d_{deklaag}` ter plaatse van het uittredepunt is gedefinieerd als de verticale afstand tussen het maaiveldniveau en de bovenkant van de pipinggevoelige zandlaag:

.. math::

   d_{deklaag} = mv_{exit} - top_{zandlaag}

waarin:
- :math:`mv_{exit}` maaiveldniveau ter plaatse van het uittredepunt [m+NAP]
- :math:`top_{zandlaag}` niveau bovenkant van de pipinggevoelige zandlaag [m+NAP]

De stijghoogte ter plaatse van het uittredepunt :math:`\phi_{exit}` [m+NAP] wordt volgens de schematiseringshandleiding :cite:`sh_piping_2021` beschreven door:

.. math::

   \phi_{exit} = \phi_{polder} + r_{exit} \cdot (h_{rivier} - \phi_{polder})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]
- :math:`r_{exit}` de dempingsfactor ter plaatse van het uittredepunt [-]
- :math:`h_{rivier}` het waterniveau in de rivier [m+NAP]

De dempingsfactor :math:`r_{exit}` ter plaatse van het uittredepunt is afhankelijk van de locatie van het uittredepunt ten opzichte van de dijk en de geohydrologische situatie. De schematiseringshandleiding piping :cite:`sh_piping_2021` hanteert dit als een onafhankelijke invoerparameter.

:math:`h_{exit}` is de randvoorwaarde in het uittredepunt, gedefinieerd door het maximum van het polderpeil en het maaiveldniveau ter plaatse van het uittredepunt:

.. math::

   h_{exit} = max(\phi_{polder}, mv_{exit})

waarin:

- :math:`\phi_{polder}` het waterniveau in de polder [m+NAP]


Heave
~~~~~

De grenstoestandfunctie van **heave** :math:`Z_{h}` is in :cite:`sh_piping_2021` als volgt gedefinieerd:

.. math::

   Z_{h} = m_{h} \cdot i_{i,c} - \frac{\phi_{exit} - h_{exit}}{d_{deklaag}}

waarin:

- :math:`m_{h}` de modelfactor voor heave is [-]
- :math:`i_{i,c}` de kritieke heave-gradiënt is [-]

Opgemerkt wordt dat de modelfactoren :math:`m_{u}` en :math:`m_{h}` niet zijn opgenomen in de formules van de schematiseringshandleiding piping :cite:`sh_piping_2021`, maar wel in deze implementatie zijn opgenomen om de modelonzekerheid expliciet te kunnen kwantificeren.


Terugschrijdende erosie
~~~~~~~~~~~~~~~~~~~~~~~

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

- :math:`L_{kwelweg}` de kwelweglengte is [m], gedefinieerd als de horizontale afstand tussen het uittredepunt en een onzeker intredepunt.
- :math:`\eta` coëfficiënt van White (sleepkrachtfactor) [-]. Standaardwaarde is 0.25
- :math:`\gamma_{korrel}` volumieke dichtheid van zand [kN/m³]. Standaardwaarde is 26.0 kN/m³
- :math:`\gamma_{w}` het volumegewicht van water [kN/m³]
- :math:`\theta` de rolweerstandshoek van zandkorrels van de aangepaste Sellmeijer-rekenregel [°]. Standaardwaarde is 37°
- :math:`d_{70,m}` de referentie- :math:`d_{70}`-waarde [m]. Standaardwaarde is 2.08E-4 m
- :math:`d_{70}` de 70-percentielwaarde van de korrelverdeling van de pipinggevoelige laag [m]
- :math:`k` de Darcy-doorlatendheid van de zandlaag [m/s]
- :math:`\upsilon_{w}` de kinematische viscositeit van water [m²/s]. Standaardwaarde is 1.33E-6 m²/s bij 10°C
- :math:`g` de zwaartekrachtversnelling [m/s²]. Standaardwaarde is 9.81 m/s²
- :math:`D_{wvp}` de dikte van de watervoerende zandlaag [m]
