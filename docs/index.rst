.. GeoProb-Pipe documentation master file, created by
   sphinx-quickstart on Fri Mar 28 16:05:34 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


**GeoProb-Pipe** is a Python app om probabilistische pipingberekeningen uit te voeren. De grenstoestandfuncties zijn aangepast zodat de respons in het watervoerende pakket beschreven wordt door model4a van het Technisch Rapport Waterspanningen bij Dijken :cite:`trw_2004`. Deze documentatie is bedoeld om de gebruiker achtergronden te geven bij keuzes die gemaakt zijn bij de implementatie van de grenstoestandfuncties en de analytische oplossing van het stationaire model. De documentatie is ook bedoeld voor ontwikkelaars die de bibliotheek verder willen ontwikkelen.

Gebruik
-------

De methode gaat uit van (in principe) een oneindig aantal mogelijke locaties van wellen (of uittredepunten) die een onbekende bijdrage kunnen hebben aan de overstromingskans van een dijktraject. Meer informatie is te vinden in onderstaande link. 

.. toctree::
   :maxdepth: 2

   background/uittredepuntenmethode

Achtergronden
-------------

In dit deel van de documentatie zijn de achtergronden beschreven van de implementatie van de functies die in deze bibliotheek zijn opgenomen.

.. toctree::
   :maxdepth: 2

   background/uittredepuntenmethode
   background/stationair_model
   background/piping
   background/grenstoestandfuncties
   

API
---

.. toctree::
   :maxdepth: 2

   dev/overview


Referenties
-----------

.. toctree::
   :maxdepth: 2

   references

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
