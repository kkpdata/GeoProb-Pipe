Probabilistische rekenmethoden
==============================

`GeoProb-Pipe` maakt gebruik van de Probabilistic Library <https://github.com/Deltares/ProbabilisticLibrary>`_.

Voor `GeoProb-Pipe` zijn de belangrijkste probabilistische rekenmethodieken `FORM` en `Importance Sampling`. 
De documentatie van de Probabilistic Library bevat informatie over de beschikbare rekenmethodieken.

In de huidige implementatie zijn de rekeninstellingen hard-coded geprogrammeerd in de broncode van `GeoProb-Pipe`.
De aparte grenstoestandfuncties (uplift, heave en terugschrijdende erosie) worden per scenarioberekening geëvalueerd 
met `FORM` en vervolgens gecombineerd met `Importance Sampling`.

Voor `FORM` zijn de rekeninstellingen:

* "variation_coefficient": 0.02
* "maximum_iterations": 1000
* "relaxation_factor": 0.4
* "reuse_calculations": False

Voor `Importance Sampling` zijn er geen afwijkende rekeninstellingen gedefinieerd.

Deze rekenmethodieken worden toegepast in een rekenprocedure, zie :ref:`rekenprotocol`.