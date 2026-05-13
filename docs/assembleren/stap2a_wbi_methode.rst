WBI-methode
===========

Ten tijde van de introductie van het Wettelijk Beoordelingsinstrumentarium (WBI) was volledig probabilistisch
combineren van elementen niet beschikbaar. Ook omdat er veel faalmechanismen waren zonder probabilistische benadering.
``Er is daarom een methode bedacht`` die de trajectkans benadert, rekening houdend met een verondersteld lengte-effect.

Hierbij zijn een aantal aannames gedaan, namelijk:

1. Doorsneden binnen een vak zijn statistisch homogeen.

2. Voor ieder faalmechanisme is een equivalente onafhankelijke lengte bepaald. Dit is een opschaalfactor die zorgt voor
   min of meer onafhankelijke vakken in een dijktraject.

3. ``De opgeschaalde elementen`` zijn onafhankelijk verondersteld voor geotechnische faalmechanismen.

Voor piping is de equivalente onafhankelijke lengte :math:`ΔL` tussen de 100 en 300 m. In vergelijking met de methode
van Hydra-Ring levert deze methode een iets conservatievere trajectkans omdat vakken als onafhankelijk worden
verondersteld.

In GeoProb-Pipe is bij de initiële assemblage het uitgangspunt dat het hele vak pipinggevoelig is (``a=1``) en dat de
onafhankelijke lengte :math:`ΔL` gelijk is aan 300 m. Dit levert een lichte conservatieve schatting op. ``De gebruiker``
``kan aan de hand van de resultaten controleren of dit uitgangspunt klopt``.

.. todo::

    Onderstaande warning oplossen.


.. warning::

    TODO:

    - De zinsnede ``Er is daarom een methode bedacht`` laat in het midden of wij dat hebben bedacht of dat dat ergens
      anders vandaan komt. We moeten hier op zijn minst aangeven welke, met bij voorkeur ook een volledige
      bronvermelding.

    - Wat zijn de ``De opgeschaalde elementen`` precies?

    - Parameter ``a`` wordt ineens geïntroduceerd en zonder zijn rol duidelijk te maken.

    - ``De gebruiker kan aan de hand van de resultaten controleren of dit uitgangspunt klopt`` Hoe doet de gebruiker
      dit? Dit staat niet in de tekst.

    - Er is verteld over de WBI-methode, maar niet uitgelegd hoe de trajectfaalkans berekend wordt. S.v.p. in
      formulevorm toevoegen.
