Typen ondergrondscenario's
==========================

Een ondergrondscenario is een unieke verzameling van variabelen die de eigenschappen van de ondergrond beschrijven. 
Ondergrondscenario's worden per vak of per uittredepunt vastgelegd. Specifiek voor het mechanisme piping zijn de 
ligging en de eigenschappen van watervoerende zandlaag van belang. In hoofdlijn zijn er drie typen ondergrondscenario's:

- Holoceen gefundeerd (HLF): Hierbij zit de deklaag boven een holocene zandlaag welke samen met de onderliggende 
  pleistocene zandlaag het watervoerend pakket vormen.
- Pleistoceen (PL): Hierbij ligt de deklaag direct boven op een pleistocene zandlaag.
- Tussenzandlaag: Hierbij is er nog een tussenzandlaag aanwezig omsloten door de deklaag en een andere kleilaag. 
  Deze is niet in direct contact met het pleistocene watervoerend pakket.

Een kenmerk van ondergrondscenario's is dat ze elkaar uitsluiten. Ter plaatse van een uittredepunt komt of het ene 
scenario voor binnen een vak of het andere. We kiezen er in deze implementatie voor om per vak een ondergrondscenario 
vast te leggen. Dit betekent dat alle uittredepunten binnen een vak dezelfde (typen) ondergrondscenario's hebben. Wel 
is het mogelijk om de eigenschappen van de ondergrond per uittredepunt te variëren. Dit overschrijft de eigenschappen 
op vakniveau.

.. figure:: /_static/TypenOndergrondscenario.png
   :width: 100%

   Voorbeeld typen ondergrondscenario's
