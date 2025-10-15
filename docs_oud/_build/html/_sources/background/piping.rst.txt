##########
Sellmeijer
##########

De formulering van Sellmeijer zoals die gedefinieerd is in het WBI2017 is:

.. math::
    
    \Delta H = L F_{resistance} F_{scale} F_{geometry}

waarbij:

.. math::
    
    F_{resistance} = \eta \cdot (\frac{(26.0 - \gamma_{w})}{\gamma_{w}}) \tan(\theta)

    F_{scale} = \frac{d_{70.m}}{\sqrt[3]{\kappa L}} \frac{d_{70}}{d_{70.m}}^{0.4}  

    F_{geometry} = 0.91 \frac{D}{L}^{\frac{0.28}{(\frac{D}{L})^{2.8} - 1} + 0.04}

    \kappa = \frac{\upsilon}{g} \cdot k = 1.35 \cdot 10^{-6} \cdot k

waarbij:

- :math:`\Delta H` = kritiek verval in m
- :math:`L` = Kwelwelengte in m
- :math:`\eta` = Coëfficiënt van White (sleepkrachtfactor) = 0.25
- :math:`\gamma_{w}` = soortelijk gewicht van het water in kN/m³
- :math:`\theta` = Rolweerstandshoek van zandkorrels in graden
- :math:`d_{70.m}` = referentiewaarde van de korrelgrootte in m
- :math:`\kappa` = intrinsieke doorlatendheid in m\ :sup:`2`
- :math:`\upsilon` = kinematische viscositeit van grondwater van 10\ :sup:`o` Celsius  in m²/s
- :math:`g` = valversnelling van de zwaartekracht in m/s²
- :math:`k` = doorlatendheid in m/s
- :math:`d_{70}` = 70-percentiel waarde van de korrelverdeling van de piping gevoelige laag in m
- :math:`D` = dikte van de zandlaag in m

In de schematiseringshandleiding van het WBI2017 :cite:t:`sh_piping_2021` staat een formulering van de rekenregel van Sellmeijer die afwijkt van de implementatie in de WBI-software. De afwijking zit in de definitie van de weerstandsfactor :math:`F_{resistance}`. In de schematiseringshandleiding is de weerstandsfactor gedefinieerd als:

.. math::
    
    F_{resistance} = \eta \cdot (\frac{16.5}{\gamma_{w}}) \tan(\theta)


