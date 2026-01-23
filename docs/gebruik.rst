Gebruik applicatie
==================

GeoProb-Pipe is een command line-applicatie met een eenvoudig **installatieproces**. Je begint met het aanmaken van een
nieuwe virtuele Python-omgeving en installeert vervolgens de ``geoprob_pipe``-package. Zie de paragraaf
:ref:`installatie` voor meer details.

Tijdens het **pre-processen** bereid je de invoerdata voor. De applicatie begeleidt je stap voor stap door het proces.
In de paragraaf :ref:`pre-processing` wordt dit verder toegelicht. Het resultaat van deze stap is een
``.geoprob_pipe.gpkp``-bestand waarin alle invoer geografisch is gerefereerd en geschikt is voor gebruik als GeoPackage
in QGIS of ArcGIS.

Na het pre-processen vraagt GeoProb-Pipe of je de **probabilistische berekeningen** wilt uitvoeren. Deze stap bestaat
uitsluitend uit rekentijd. De resultaten van de berekeningen worden toegevoegd aan het ``.geoprob_pipe.gpkp``-bestand.

Tijdens het **post-processen** worden alle resultaten geëxporteerd, waaronder ruwe data en visualisaties.

.. toctree::
    :maxdepth: 2
    :caption: Inhoud
    :titlesonly:

    gebruik/keuze_menu
    gebruik/invoer
    gebruik/uitvoer
    gebruik/projectbestanden_vergelijken
    gebruik/enkele_berekening_inspecteren
    gebruik/inladen_in_qgis
    gebruik/inladen_in_db_browser



