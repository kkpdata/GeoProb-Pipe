#####################
Grenstoestandfuncties
#####################

Grenstoestandfuncties WBI
=========================

In :cite:`sh_piping_2021` en :cite:`calibration_piping_2016` zijn de grenstoestandfuncties gedefinieerd zoals het basisinstrumentariumd die hanteert. Falen treedt op als de grenstoestandfuncties van opbarsten, heave en piping bereikt zijn.




Grenstoestandfuncties met model 4a
==================================

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


------------------------------
Grenstoestandfunctie opbarsten
------------------------------

De grenstoestandfunctie voor opbarsten :cite:`calibration_piping_2016` is gedefinieerd als:

.. math::
    
    Z_{o} = m_{u} \cdot \Delta H_{c} - (h -h_{exit} - r_{c} \cdot D_{cover})

--------------------------
Grenstoestandfunctie heave
--------------------------

De grenstoestandfunctie voor heave :cite:`calibration_piping_2016` is gedefinieerd als:

.. math::
    
    Z_{h} = m_{h} \cdot \Delta H_{c} - (h -h_{exit} - r_{c} \cdot D_{cover})

---------------------------
Grenstoestandfunctie piping
---------------------------

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


--------------------
Lijst van variabelen
--------------------

WBI rekenkernel piping
Benodigde invoer


Rekenkernel met model 4a


Benodigde invoer


Rekenkernel met tijdsafhankelijke respons van de stijghoogte



Benodigde invoer


.. bibliography