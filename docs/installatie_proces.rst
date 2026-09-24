
Installatie proces
==================

De installatie en het gebruik van `GeoProb-Pipe` is eenvoudig en wordt hieronder toegelicht.

Start een schone Python environment. `GeoProb-Pipe` is ontwikkelt op Python 3.12. Deze versie wordt aangeraden voor
gebruik. Voer daarna het volgende commando's uit om `GeoProb-Pipe` te installeren vanuit de
`Python Package Index <https://pypi.org/project/geoprob_pipe/>`_. De onderliggende
`probabilistische bibliotheek <https://pypi.org/project/probabilistic-library/>`_ wordt automatisch als afhankelijkheid mee geïnstalleerd.


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

GeoProb-Pipe slaat in het GeoPackage-bestand (met de extensie ``.geoprob_pipe.gpkg``) de versie van GeoProb-Pipe op als
metadata. Deze informatie wordt bij het initiële gebruik van het bestand opgeslagen. De informatie kan worden
gebruikt om achteraf te zien met welke Python-packageversies het bestand is aangemaakt.

De huidige implementatie biedt nog geen geautomatiseerde manier om op basis hiervan de Python-installatie te
reconstrueren. Backwards compatibility van ieder GeoProb-Pipe-bestand kan daarom niet worden gegarandeerd.


.. note::
   De opgeslagen packageversies zijn uitsluitend metadata. Gebruik voor het reconstrueren van een omgeving een
   handmatig samengesteld ``requirements.txt``-bestand; deze functionaliteit wordt niet automatisch door GeoProb-Pipe
   uitgevoerd.


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

