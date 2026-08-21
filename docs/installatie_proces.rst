
Installatie proces
==================

De installatie en het gebruik van `GeoProb-Pipe` is eenvoudig en wordt hieronder toegelicht.

Start een schone Python environment. `GeoProb-Pipe` is ontwikkelt op Python 3.12. Deze versie wordt aangeraden voor
gebruik. Voer daarna het volgende commando's uit om `GeoProb-Pipe` te installeren vanuit de
`Python Package Index <https://pypi.org/project/geoprob_pipe/>`_. De onderliggende
`probabilistische bibliotheek <https://pypi.org/project/probabilistic-library/>`_ (PTK-tool wrapper) wordt automatisch
mee geïnstalleerd.


.. code-block:: bash

    pip install geoprob_pipe


Daarna start je de applicatie met het commando. Zorg er voor dat je Python-environment actief is.

.. code-block:: bash

    geoprob_pipe

Na het opstarten van de applicatie begeleidt `GeoProb-Pipe` je door het gebruik. Je kunt op elk moment de applicatie
afsluiten, en weer opstarten. Meestal geeft de applicatie je de mogelijkheid om af te sluiten, is dit niet het geval,
dan kun je dat doen middels de toetsencombinatie ``ctrl + c``.


Backwards compatibility
^^^^^^^^^^^^^^^^^^^^^^^

GeoProb-Pipe slaat in het GeoPackage-bestand (met .geoprob_pipe.gpkg-extensie) de gebruikte Python package-versies op,
inclusief de gebruikte versie van GeoProb-Pipe. Dit maakt het mogelijk om van elk GeoProb-Pipe-bestand de Python
installatie te reconstrueren. Op deze manier wordt backwards compatibility gegarandeerd. Je reconstrueert de Python
installatie op de volgende wijze.


.. note::
   Deze sectie van de documentatie is nog niet volledig en wordt binnenkort uitgebreid.

   Er wordt momenteel namelijk overwogen of de `pip freeze`, die als `dict` is opgeslagen in de GeoPackage, op een
   minder omslachtige manier kan worden opgeslagen t.b.v. installatie.

.. TODO: Note van hierboven oppakken. Overweeg de volgende ideeën:
 - Wellicht is het mogelijk om de pip freeze als multiline op te slaan in de database? Dan kan de gebruiker die direct
   opslaan in een requirements.txt-bestand en installeren via pip install -r requirements.txt.
 - In documentatie ook tip geven om eerst eens de applicatie versie te installeren via pip install
   geoprob-pipe==version, waarbij de version ook gewoon in de geopackage te lezen is.
 - Sla de pip freeze op voor initieel gebruik (bij invoer), en voor laatste rekenslag. Nu is die alleen voor initieel.
   Dus het kan zijn dat het helemaal niet backwards compatible is.


Upgraden, beschikbare versies en changelog
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Heb je GeoProb-Pipe al geïnstalleerd maar wil je upgraden naar de laatste versie? Dat doe je met het volgende commando.

.. code-block:: bash

    pip install --upgrade geoprob_pipe

Wil je een specifieke versie installeren? In de `Python Package Index <https://pypi.org/project/geoprob_pipe/#history>`_
zie je de release history. Je kunt vervolgens een specifieke versie installeren middels dit commando.

.. code-block:: bash

    pip install geoprob_pipe==1.4.1

Vervang het versie nummer met jou gewenste versie. In het
`changelog-bestand <https://github.com/kkpdata/GeoProb-Pipe/blob/alpha/geoprob_pipe/changelog.py>`_ zie je korte
release notes per versie.

