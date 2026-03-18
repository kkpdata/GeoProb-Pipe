Assembleren
===========

Deze pagina beschrijft de assemblage van faalkansen binnen `GeoProb-Pipe`
voor het faalmechanisme STPH (piping).
De assemblage combineert lokaal berekende faalkansen op uittredepuntniveau
tot faalkansen op vak- en trajectniveau.

Samenvatting
------------

De assemblage start bij individuele scenario’s per uittredepunt, waarin
meerdere faalmechanismen probabilistisch worden gecombineerd.
Via opschaling met het lengte-effect worden faalkansen geaggregeerd naar
vakniveau. Op trajectniveau worden vakkansen gecombineerd als een
seriesysteem, zonder aanvullende opschaling.

Het lengte-effect wordt uitsluitend toegepast bij de overgang van
uittredepunt naar vak, waarmee dubbeltelling wordt voorkomen. De
α-vector wordt niet gemiddeld of gecombineerd, maar steeds ontleend aan
het onderliggende scenario, uittredepunt of vak dat de grootste bijdrage
levert aan de totale faalkans, omdat α-vectoren niet lineair
optelbaar zijn.

.. toctree::
   :maxdepth: 2
   :caption: Inhoud
   :titlesonly:
    
   assembleren/kader
   assembleren/stap0_sc
   assembleren/stap1_sc_up
   assembleren/stap2_up_vak
   assembleren/stap3_vak_tra