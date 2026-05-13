Faalkans vak- en trajectniveau
==============================

.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO: Paragraaftitel geeft aan dat dit over vak- en trajectniveau gaat. Maar we gaan direct vol in op trajectniveau.
    Er mist dus een introductie van deze paragraaf (om toe te lichten waar ook vakniveau besproken wordt).


De faalkans van een dijktraject wordt in GeoProb-Pipe opgebouwd vanuit individuele uittredepunten die samen een
seriesysteem vormen. Elk uittredepunt representeert een mogelijke locatie waar piping kan optreden, maar doordat deze
punten ruimtelijk dicht bij elkaar kunnen liggen is er sprake van onderlinge afhankelijkheid. Deze afhankelijkheid
bepaalt ``in sterke mate`` de trajectkans, maar in de praktijk is de exacte mate niet bekend. Hierdoor is het
onverstandig om de trajectfaalkans rechtstreeks te bepalen uit het combineren van de uittredepuntkansen, maar moet deze
worden benaderd binnen een bandbreedte die wordt begrensd door twee uitersten.


.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO: Hierboven staat 'in sterke mate'. Maar het is niet onderbouwd dat dit of waarom dit een sterke
    afhankelijkheid heeft. De tekst zelf geeft de lezer daar geen aanleiding toe dat te denken. Bronvermelding opnemen?
    Of nadere uitleg in een apart blokje?


- **Bovengrens faalkans**

  Hierbij ga je uit van een volledige onafhankelijkheid tussen de uittredepunten, wat leidt tot een conservatieve
  inschatting (sommeren van faalkansen).


- **Ondergrens**

  Hierbij ga je uit van een volledige afhankelijkheid tussen de uittredepunten, wat leidt tot een minimale
  trajectfaalkans. Je neemt de maximale faalkans in plaats van dat je sommeert.


- **Werkelijkheid**

  De elementen (uittredepunten) in het seriesysteem hebben op voorhand een onbekende onderlinge afhankelijkheid.
  De mate van afhankelijkheid bepaalt de ‘werkelijke’ faalkans van het systeem. ``Echter, deze``
  ``werkelijke faalkans is in de praktijk lastig te bepalen vanwege beperkingen in rekenkracht en geheugen, maar ook door``
  ``beperkingen in beschikbare rekentechnieken.`` Daarom ligt de werkelijke situatie tussen de twee uitersten, maar
  kan deze niet exact worden vastgesteld.

.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO: Hierboven staat 'De mate van afhankelijkheid'. Maar als ik de tekst zo lees zou ik zeggen dat 'de van
    afhankelijkheid' vooral afhangt van kennis over het uittredepunt, en dat het grote aantal uittredepunten
    ons het onmogelijk maakt om deze afhankelijkheid precies op te nemen.

    Want voor mijn gevoel kun je bijvoorbeeld binnen een vak alle uittredepunten van een sloot groeperen (max),
    maar de onafhankelijke punten binnen het vak (met ééntje voor de sloot), sommeren.

    Deze uitspraak roept dus twijfels op.




Waarom niet volledig probabilistisch combineren?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bij de uittredepuntenmethode wordt een significant aantal doorsneden doorgerekend. Als de dichtheid van uittredepunten
groot genoeg is, is het voor het bepalen van de trajectkans voldoende om de uittredepunten te combineren op basis van
onderlinge correlatie. Dan is er geen opschaling nodig onder de aanname van statistisch homogene vakken. Een
voorwaarde is dat er geschikte probabilistische rekentechnieken toepasbaar zijn. Deze probabilistische rekentechnieken
zijn beschikbaar maar beperkt toegankelijk en rekenintensief, waardoor dit ``nog niet is geïmplementeerd in GeoProb-Pipe``.

.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO: Is dit wat we later willen doen en bedoelen met 'volledig probabilistisch` combineren?



In plaats daarvan zijn in eerdere projecten, zoals VNK-2 en de implementatie in Hydra-Ring, benaderingen ontwikkeld die
uitgaan van statistisch homogene vakken. Binnen deze aanpak wordt de kans van een individuele doorsnede opgeschaald
naar een vakkans via de ``outcrossing-methode``, waarna vakkansen worden gecombineerd met de
``Hohenbichler-Rackwitz-methode``. Deze aanpak vereist dat vakken voldoende groot zijn om ``beperkte onderlinge``
``afhankelijkheid te garanderen``, maar kan onnauwkeurigheden introduceren bij sterke correlaties tussen vakken. Daarom is
het toepassen ervan afhankelijk van de beschikbaarheid van betrouwbare probabilistische invoer en goed gedefinieerde
correlatiestructuren. Waar Hydra-Ring uitgaat van expliciete probabilistische modellering van afhankelijkheid tussen
doorsneden, benadert de ``WBI-methode`` dit effect indirect via ``een equivalente onafhankelijke lengte en een``
``veronderstelde vakindeling``.

Binnen dit kader zijn in GeoProb-Pipe drie methoden geïmplementeerd om de trajectkans te benaderen, elk met een eigen
manier om met lengte-effect en afhankelijkheid tussen uittredepunten om te gaan: de WBI-methode, de Window-methode en
het opschalen van individuele secties.


.. toctree::
   :maxdepth: 1

   stap2a_wbi_methode
   stap2b_window_methode
   stap2c_individuele_secties

.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO:

    - De outcrossing methode en Hohenbichler-Rackwitz-methode verdient uitleg, wellicht onder een eigen kopje.

    - ``beperkte onderlinge afhankelijkheid te garanderen``. Als ik de zin lees zou ik verwachten dat het gaat om
      beperkte onafhankelijkheid onderling te garanderen. Hoe zit dit precies?

    - WBI-methode wordt ineens uit het niets geïntroduceerd.

    - Wat is het verschil tussen ``een equivalente onafhankelijke lengte`` en ``een veronderstelde vakindeling``?

