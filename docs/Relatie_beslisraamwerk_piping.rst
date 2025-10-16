Relatie beslissingsondersteunend raamwerk piping
================================================

Het Beslissingsondersteunend Raamwerk Piping (BRP) :cite:t:`BRP_2024` beschrijft een aanpak om aspecten te beschouwen die niet expliciet in de rekenregels zijn opgenomen. 
Voor bepaling van de overstromingskans van het faalmechanisme piping is het belangrijk om ook deze aanvullende aspecten te beschouwen. 

In het BRP zijn 14 factsheets opgenomen die factoren beschrijven die het optreden van piping beïnvloeden. Daarnaast worden handelingsperspectieven gegeven om met deze factoren om te gaan.
Deze handleiding beschrijft hoe deze aspecten rekenkundig kunnen worden meegenomen in de overstromingskansberekening met `GeoProb-Pipe`.
Het kennisniveau van elk aspect bepaalt de mate van implementatie in `GeoProb-Pipe`.

1. Opbarsten: Sterkte deklaag
Het is erg aannemelijk dat de deklaag enige weerstand tegen scheuren biedt.
Omdat de scheurbestendigheid nog niet kwantitatief kan worden bepaald en er geen gevalideerd model beschikbaar is,
is dit aspect niet geïmplementeerd in `GeoProb-Pipe`.
Wel kan via een modelfactor opbarsten :math:`m_{u}` gebruikt kunnen worden om gevoeligheidsberekeningen te doen.

2. Opbarsten: Tijdsafhankelijke stroming en overige geohydrologische invloeden (aspect 2 en 3 uit BRP)
Grondwaterstroming is een bekend en goed bestudeerd fenomeen. Met numerieke 
berekeningen kan het effect van een kortdurend hoogwater op de stijghoogte worden 
bepaald. Binnen `GeoProb-Pipe` is het rekenmodel voor de stijghoogte flexibel opgezet, zodat
andere stijghoogtemodellen kunnen worden toegepast.

4. Terugschrijdende erosie: Aanwezigheid voorland (> 1 keer dijkbasis)
Het meenemen van voorlanden sluit aan op de algemeen bekende 
grondwaterstromingstheorie. Het voorland kan al meegenomen in de piping analyse conform 
het BOI, er is een uitwerkingsmethode en benodigde parameters kunnen worden bepaald 
door meten en monitoren. Daarnaast is mogelijk numerieke sommen te maken en er is een 
methode om het analytisch mee te nemen. 
`GeoProb-Pipe` neemt het voorland mee en voert geen controle uit op pipegroei.

.. TODO: je doelt hier denk ik op de stijghoogtemodellen toch? en met voert geen controe uit op pipegroei -> je bedoelt dat we geen controle uitvoeren op de lengte van de pipegroei ten opzicht van de dijkbasis max?
.. twijfel over dat laatste stukje kun je die iets verduidelijken?

5. Terugschrijdende erosie: Fijne fractie
De weerstand tegen erosie van zand met veel fijne fractie is theoretisch onderbouwd.
Specifiek voor piping in getijdenzand zijn er in Nederland op verschillende schalen ca. 35 
experimenten uitgevoerd om de hypothese te bewijzen en kwantificeren.Uit recente proeven met getijdenzand :cite:`getijdenzand_2023` blijkt dat deze grondsoorten
een aanzienlijk hogere weerstand tegen terugschrijdende erosie vertonen dan rivierzanden.
Dit wordt veroorzaakt door de aanwezigheid van fijne fracties, slechtere sortering en gedeeltelijke
cementatie, die gezamenlijk leiden tot een hogere kritieke gradiënt.
`GeoProb-Pipe` houdt rekening met de aanwezigheid van een fijne fractie in de door het toevoegen van een modelfactor :math:`m_{ff}` naast de modelfactor terugschrijdende erosie :math:`m_{p}`.

6. Terugschrijdende erosie: Slechte sortering (korrelgrootteverdeling)
Er zijn experimentenseries met variaties in uniformiteitscoëfficiënt (Cu). Er is echter geen eenduidig beeld van de invloed van de sortering op het kritiek verval. Dit aspect is daarom niet meegenomen in `GeoProb-Pipe`.

7. Terugschrijdende erosie: Drukval in opbarstkanaal (hoger of lager dan 0.3d)
De theorie dat er weerstand in het opbarstkanaal aanwezig is, is met veldmetingen en 
experimenteel onderbouwd. Echter is in de praktijk moeilijk te 
voorspellen hoe groot de weerstand zal zijn. Gedurende het piping proces zal de weerstand 
in het kanaal veranderen doordat de stroomsnelheid toeneemt en de korrels uit het 
opbarstkanaal spoelen. De vorm van het opbarstkanaal is ook van grote invloed, echter is het 
formaat van het opbarstkanaal eveneens moeilijk te voorspellen. 
`GeoProb-Pipe` houdt rekening met de weerstand in het opbarstkanaal door de reductieconstante van het verval over de deklaag :math:`r_{c,deklaag}` als een stochast te definiëren. 

8. Terugschrijdende erosie: Heterogeniteit korrelgrootte in baan van de pijp
Het is algemeen bekend dat de ondergrond op korrelschaal heterogeen is. De pipe volgt de 
weg van de minste weerstand en meandert hierdoor. In dit proces is primaire erosie van 
belang, echter is dit moeilijk te voorspellen. Er zijn voor zover bekend geen experimenten 
met sterk heterogene ondergronden. Wel zijn er proefvelden met metingen. Ook zijn er 
numerieke berekeningen met heterogeniteit waaruit blijkt dat de sterkste korrel in het zwakste 
pad ongeveer overeen komt met de gemiddelde d70. In de praktijk is het ook moeilijk om de 
heterogeniteit goed in kaart te brengen of te karakteriseren, dit maakt de inschatting van het 
effect moeilijk.
`GeoProb-Pipe` biedt de mogelijkheid om de :math:`d_{70}` als een stochast te definiëren.

9. Terugschrijdende erosie: Fluctuatie van de diepte of helling van de deklaag in de baan van de pipe. 
Het effect van de helling is theoretisch onderbouwd en er is een erosie model dat ook in de rekenregel toegepast zou kunnen worden. Daarnaast zijn er enkele experimenten ter validatie van deze theorie. Toch is deze kennis nog niet 
algemeen toepasbaar en te generaliseren, omdat het slechts enkele experimenten betreft.
`GeoProb-Pipe` biedt geen mogelijkheden om dit aspect mee te nemen.


10. Terugschrijdende erosie: 3D concentratie van stroming naar de pipe
In een aantal kleine schaal laboratoriumproeven is het kritieke verval in 3D ca. 1/2 zo groot 
als met de 2D regel van Sellmeijer wordt voorspeld. In deze proeven vormt één pipe en is 
geen afstroming naar het achterland.
Er is weinig informatie over het effect op grotere schaal, al wordt op basis van theorie 
verwacht dat de invloed van 3D stroming groter kan zijn leidend tot lager kritiek verval. Op basis van 
de geohydrologie en experimenten wordt verwacht dat de invloed van het 3D effect kleiner 
wordt bij doorlatendere achterlanden.
Vanwege de verwachte grote invloed van dit aspect is er in `GeoProb-Pipe` de mogelijkheid om een modelfactor 3D :math:`m_{3D}` te gebruiken.


11. Terugschrijdende erosie: Tijdsafhankelijkheid
In het promotie onderzoek van Joost Pol is uitgebreid onderzoek gedaan naar 
tijdsafhankelijke pipegroei met kleine en grote schaal experimenten, numerieke modellen en 
er is een statistisch uitgewerkte methode voorgesteld. Voor de toepassing op grotere schaal 
zijn er nog onzekerheden. Het is soms lastig vast te stellen of er nog oude pipes aanwezig 
zijn en 3D numerieke modellen geven op grote schaal onverwachte resultaten voor het kritiek 
verval. 
`GeoProb-Pipe` heeft geen implementatie van dit aspect. Wel zou via een modelfactor terugschrijdende erosie :math:`m_{p}` gebruikt kunnen worden om gevoeligheidsberekeningen te doen.


12. Terugschrijdende erosie: Anisotropie van de doorlatendheid
Grondwaterstromingstheorie met anisotropie is goed bekend: voor het bepalen van het effect 
op stroming kunnen daarom numerieke berekeningen uitgevoerd worden. Daarnaast is er 
een toevoeging op de rekenregel van Sellmeijer, waarmee een eerste inschatting gemaakt 
kan worden van de invloed van anisotropie. Experimentele validatie met anisotrope ondergrond ontbreekt tot op heden
`GeoProb-Pipe` biedt de mogelijkheid om het effect van anisotropie op het kritieke verval te verrekenen door middel van een modelfactor :math:`m_{aniso}`.

13. Terugschrijdende erosie: Meerlaagsheid watervoerend pakket (ten opzichte van 
gewogen gemiddelde)
Grondwaterstroming is een bekend fenomeen, met weinig onzekerheden. Zo geldt dat ook 
voor meerlaagse stroming. De stroming naar de pipe toe is numeriek (met D-GeoFlow) goed 
te bepalen. Echter is het zo dat er slechts enkele fysieke experimenten zijn die de invloed 
van meerlaagsheid op piping bevestigen. Het is mogelijk dat een verandering in verticale 
instroming de secundaire en primaire erosie beïnvloed op een manier die niet in numerieke 
analyses meegenomen wordt.
`GeoProb-Pipe` heeft hiervoor een aparte modelfactor meerlaagsheid :math:`m_{ml}` geïmplementeerd.

14. Vervolgprocessen: Duur van het bezwijkproces
Op globale lijn zijn de vervolgprocessen bekend. Tijdens de IJkdijkproeven is het 
proces geobserveerd. De duur en observaties staan beschreven. Maar deze resultaten zijn niet te generaliseren, er is geen hypothese of model voor de duur van deze vervolgprocessen bij dijken in de praktijk. Internationaal zijn er numerieke modellen waarmee de duur van het bezwijkproces bij dammen berekend kan worden, echter zijn deze niet gevalideerd voor dijken zoals we die in Nederland hebben. Daarom is dit aspect niet meegenomen in `GeoProb-Pipe`.




