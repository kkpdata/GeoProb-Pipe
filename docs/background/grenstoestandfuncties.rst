#####################
Grenstoestandfuncties
#####################

In :cite:`sh_piping_2021` en :cite:`calibration_piping_2016` zijn de grenstoestandfuncties gedefinieerd zoals het basisinstrumentariumd die hanteert. Falen treedt op als de grenstoestandfuncties van opbarsten, heave en piping bereikt zijn.
Deze paragraaf is overgenomen uit bijlage C van :cite:`sh_piping_2021` en waarbij de variabelen hernoemd zijn naar de notatie die in deze package gehanteerd wordt, zie :ref:`Lijst van variabelen`. 

TODO: plaatje van de foutenboom toevoegen


Grenstoestandfunctie opbarsten
==============================

De grenstoestandsfunctie voor opbarsten (uplift) :math:`Z_{u}` is gebaseerd op een vergelijking van de naar beneden gerichte druk die door het gewicht van de deklaag wordt uitgeoefend (weerstand) en de naar boven gerichte waterdruk in de watervoerende zandlaag (belasting), hier uitgedrukt in vorm van een stijghoogteverschil. De grenstoestandfunctie voor opbarsten :cite:`calibration_piping_2016` is gedefinieerd als:

.. math::
    
    Z_{u} = m_{u} \cdot \Delta \phi_{c,u} - (\phi_{exit} - h_{exit})

    \Delta \phi_{c,u} = \frac{d_{deklaag} \cdot (\gamma_{sat,deklaag} - \gamma_{w})}{\gamma_{w}}


waarbij:

- :math:`Z_{u}` = grenstoestandfunctie voor opbarsten [-]
- :math:`m_{u}` = modelfactor voor opbarsten [-]
- :math:`\Delta \phi_{c,u}` = grenspotentiaal ten opzichte van maaiveld in m
- :math:`\phi_{exit}` = theoretische stijghoogte bij uittredepunt in m+NAP
- :math:`h_{exit}` = niveau van de uittredepunt in m+NAP
- :math:`d_{deklaag}` = dikte van de deklaag in m
- :math:`\gamma_{sat,deklaag}` = gemiddeld volumegewicht van de deklaag in kN/m³
- :math:`\gamma_{w}` = volumegewicht van water in kN/m³

De stijghoogte bij het uittredepunt :math:`\phi_{exit}` is binnen het WBI instrumentarium :cite:`sh_piping_2021` gedefinieerd als:

.. math::
    
    \phi_{exit} = h_{ref} + r_{exit} \cdot (h - h_{ref})

waarbij:

- :math:`h_{ref}` = polderpeil ter plaatse van uittredepunt in m+NAP
- :math:`r_{exit}` = dempingsfactor bij uittredepunt [-]
- :math:`h` = Buitenwaterstand in m+NAP


De dempingsfactor bij het uittredepunt :math:`r_{exit}` is in :cite:`sh_piping_2021` bewust niet verder gedefinieerd. In principe kan dat via grondwaterstromingsanalyses (analytisch of numeriek, stationair of tijdsafhankelijk) of expert judgement gebeuren, bij voorkeur via monitoring.

Het polderpeil :math:`h_{ref}` is de benedenstroomse randvoorwaarde. Het wordt ook het referentieniveau genoemd, 
vandaar :math:`h_{ref}`. Deze randvoorwaarde is ook belangrijk bij het afleiden van de dempingsfactor :math:`r_{exit}` op basis van peilbuismetingen. 

Bij stijgende buitenwaterstanden zal het polderpeil door kwel kunnen stijgen. Bij de schematisatie van de pipingberekeningen dient hierbij rekening gehouden te worden, bijvoorbeeld door een hogere waarde voor :math:`h_{ref}` te kiezen. In dit geval wordt de stijghoogte bij het uittredepunt :math:`\phi_{exit}` overschat. Dit is niet erg, omdat de faalkans wordt bepaald door het mechanisme piping. 

De dempingsfactor :math:`r_{exit}` op elke willekeurige locatie in het dwarsprofiel kan worden beschreven door een analytische oplossing in het geval van een stationaire situatie. De dempingsfactor :math:`r_{exit}` is dan een functie van de geometrie van het profiel (:math:`L_{voorland}`, :math:`L_{dijk}` en :math:`L_{achterland}`), de transmissiviteit :math:`kD` van het watervoerende pakket en de weerstand van het voor- en achterland (:math:`c_{voorland}` en :math:`c_{achterland}`). Zie hiervoor :ref:`stationair-model` en :cite:`sh_piping_2021`.

Grenstoestandfunctie heave
==========================

Zandtransport kan alleen optreden als de verticale uitstroomgradiënt bij het uittredepunt een
kritieke waarde voor heave overschrijdt. 
De grenstoestandfunctie voor heave :cite:`calibration_piping_2016` is gedefinieerd als:

.. math::
    
    Z_{h} = m_{h} \cdot i_{c,h} - i_{exit} = m_{h} \cdot i_{c,h} - \frac{(\phi_{exit} - h_{exit})}{d_{deklaag}}

waarbij:

- :math:`Z_{h}` = grenstoestandfunctie voor heave [-]
- :math:`m_{h}` = modelfactor voor heave [-]
- :math:`i_{c,h}` = Kritieke heave gradiënt [-]
- :math:`i_{exit}` = Optredende heave gradient [-]

In afwijking van de definitie in het WBI is ook hier consequent een modelfactor :math:`m_{u}` toegepast omdat er ook onzekerheden zijn die niet door dit model beschreven worden.

De stijghoogte in het uittredepunt :math:`\phi_{exit}` wordt beschreven door gebruik te maken van het stationaire grondwaterstromingsmodel. Dus geldt:

.. math::
..
.. \phi_{exit} = f(L_{voorland}, L_{dijk}, L_{achterland},kD,c_{voorland},c_{achterland})

Zie hiervoor :ref:`stationair-model` en :cite:`sh_piping_2021`.

Grenstoestandfunctie piping
===========================

De grenstoestandfunctie voor piping :cite:`calibration_piping_2016` is gedefinieerd als:

.. math::
    
    Z_{p} = m_{p} \cdot \Delta H_{c} - (h -h_{exit} - r_{c} \cdot D_{cover})

waarbij:

- :math:`Z_{p}` = grenstoestandfunctie voor piping [-]
- :math:`m_{p}` = modelfactor voor piping [-]
- :math:`\Delta H_{c}` = kritiek verval voor piping in m
- :math:`h` = waterstand in de rivier in m+NAP
- :math:`h_{exit}` = niveau van de uittredepunt in m+NAP
- :math:`r_{c}` = reductiefactor voor de deklaag
- :math:`D_{cover}` = dikte van de deklaag in m


Indien het model 4a geintegreerd wordt in de grenstoestandfuncties, is de respons bij het uittredepunt afhankelijk van de geometrie, de weerstand van het voorland :math:`c_{voorland}`, de transmissiviteit van het watervoerend pakket :math:`kD` en de weerstand van het achterland :math:`c_{achterland}`. 
Ook de kwelweglengte is anders gedefinieerd dan in de basisinstrumentarium. De kwelweglengte is gedefinieerd als de afstand van het uittredepunt tot het punt waar de waterstand in het watervoerend pakket gelijk is aan de waterstand in de rivier. De kwelweglengte is gedefinieerd als:

.. math::
    
    L_{kwelweg} = L_{buitenteen} + \lambda_{voorland} \cdot tanh(\frac{L_{voorland}}{\lambda_{voorland}})

    \lambda_{voorland} = \sqrt{kD \cdot c_{voorland}}

waarbij:

- :math:`L_{kwelweg}` = kwelweglengte in m
- :math:`L_{buitenteen}` = lengte van het uittredepunt tot de buitenteen in m
- :math:`\lambda_{voorland}` = de spreidingslengte van het voorland in m
- :math:`L_{voorland}` = fysiekee lengte van het voorland in m
- :math:`kD` = transmissiviteit van het watervoerend pakket in m²/d
- :math:`c_{voorland}` = weerstand van het voorland in dagen

Lijst van variabelen
====================

.. csv-table:: Lijst van variabelen
   :header: "Naam van variabele","Beschrijving","Eenheid","Type"
   :class: longtable
   :widths: 15, 50, 15, 20

    ":math:`L_{intrede}`","Afstand van uittredepunt tot geometrische intredelijn","m","Input"
    ":math:`L_{but}`","Afstand van uittredepunt tot buitenteenlijn","m","Input"
    ":math:`L_{bit}`","Afstand van uittredepunt tot binnenteenlijn","m","Input"
    ":math:`L_{achterland}`","Afstand van uittredepunt tot Achterlandlengte","m","Input"
    ":math:`mv_{exit}`","Bodemhoogte ter plaatse van uittredepunt","m+NAP","Input"
    ":math:`mv_{achterland,vak}`","Representatieve bodemhoogte achterland binnen een vak","m+NAP","Input"
    ":math:`h_{ref}`","Polderpeil ter plaatse van uittredepunt","m+NAP","Input"
    ":math:`top_{zand}`","Geschematiseerde top van het zak in het vak","m+NAP","Input"
    ":math:`\gamma_{sat,deklaag}`","Gemiddeld volumegewicht van de deklaag","kN/m^3","Input"
    ":math:`d_{deklaag}`","Dikte van de cohesieve deklaag","m","Calculated"
    ":math:`d_{deklaag,vak}`","Dikte van de cohesieve deklaag van het vak","m","Calculated"
    ":math:`\gamma_{water}`","Volumegewicht van water","kN/m^3","Constant"
    ":math:`kD_{wvp}`","Transmissiviteit van het watervoerende pakket","m^2/dag","Input"
    ":math:`D_{wvp}`","Dikte van het watervoerende pakket","m","Input"
    ":math:`k_{wvp}`","Doorlatendheid van het watervoerende pakket","m/d","Calculated"
    ":math:`d_{70}`","70% percentiel van de korrelverdeling","m","Input"
    ":math:`c_{voorland}`","Weerstand van de deklaag in het voorland","dag","Input"
    ":math:`c_{achterland}`","Weerstand van de deklaag in het achterland","dag","Input or calculated"
    ":math:`m_{u}`","modelfactor voor uplift","[-]","Input"
    ":math:`m_{h}`","modelfactor voor heave","[-]","Input"
    ":math:`m_{p}`","modelfactor voor piping","[-]","Input"
    ":math:`i_{c,h}`","Kritieke heave gradiënt","[-]","Constant"
    ":math:`r_{c,deklaag}`","Reductieconstante van het verval over de deklaag","[-]","Constant"
    ":math:`h`","Buitenwaterstand","m+NAP","Input"
    ":math:`\eta`","White's weerstandscoefficient (sleepkrachtfactor, constante van White) – Sellmeijer [-]","[-]","Constant"
    ":math:`r_{exit}`","Dempingsfactor bij uittredepunt","[-]","Calculated"
    ":math:`\phi_{exit}`","Theoretische stijghoogte bij uittredepunt","m+NAP","Calculated"
    ":math:`h_{exit}`","Benedestroomse randvoorwaarde verval","m+NAP","Calculated"
    ":math:`L_{kwelweg}`","Kwelweglengte","m","Calculated"
    ":math:`\theta`","Rolweerstandshoek – Sellmeijer","[graden]","Constant"
    ":math:`d_{70,m}`","Referentiewaarde voor de 70% percentiel van de korrelverdeling – Sellmeijer","m","Constant"
    ":math:`g`","Zwaartekrachtversnelling – 9,81 m/s²","m/s^2","Constant"
    ":math:`v_{water}`","Kinematische viscositeit water – Sellmeijer","m²/s","Constant"
    ":math:`\gamma_{k}`","Volumieke dichtheid zand onder water – Sellmeijer","kN/m^3","Constant"
    ":math:`\Delta \phi_{c,u}`","grenspotentiaal ten opzicht van maaiveld","m","Calculated"
    ":math:`\Delta h_{red}`","Gereduceerd verval","m","Calculated"
    ":math:`i_{exit}`","Optredende heave gradient","[-]","Calculated"
    ":math:`\Delta h_{c}`","Kritiek verval Sellmeijer","m","Calculated"
    ":math:`Z_u`","Grenstoestand Uplift","[-]","Calculated"
    ":math:`Z_h`","Grenstoestand Heave","[-]","Calculated"
    ":math:`Z_p`","Grenstoestand Piping","[-]","Calculated"
    ":math:`Z_{combi}`","Gecombineerde grenstoestand","[-]","Calculated"
    ":math:`L_{voorland}`","Geometrische voorlandlengte","m","Calculated"
    ":math:`L_{dijk}`","Dijkzate","m","Calculated"
    ":math:`\lambda_{voorland}`","Spreidingslengte van het voorland","m","Calculated"
    ":math:`\lambda_{achterland}`","Spreidingslengte van het achterland","m","Calculated"
    ":math:`W_{voorland}`","Geohydrologische weerstand van het voorland","m","Calculated"
    ":math:`W_{achterland}`","Geohydrologische weerstand van het achterland","m","Calculated"
    ":math:`FoS_{u}`","Veiligheidsfactor Uplift","[-]","Calculated"
    ":math:`FoS_{h}`","Veiligheidsfactor Heave","[-]","Calculated"
    ":math:`FoS_{p}`","Veiligheidsfactor Piping","[-]","Calculated"
    ":math:`k_{v,boven gws}`","Verticale doorlatendheid deklaag boven grondwaterstand","m/d","Constant"
    ":math:`k_{v,onder gws}`","Verticale doorlatendheid deklaag onder grondwaterstand","m/d","Constant"
    ":math:`gws_{m,mv}`","Grondwaterstand meters min maaiveld (scheiding verticale doorlatendheid)","m","Constant"


.. bibliography
