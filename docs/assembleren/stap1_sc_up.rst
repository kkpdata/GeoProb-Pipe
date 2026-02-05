Stap 1: Scenario → uittredepunt
================================

In GeoProb-Pipe vormt het **uittredepunt** de kleinste zelfstandige
bouwsteen in de assemblage van faalkansen.
Een uittredepunt representeert een fysieke locatie langs de waterkering
waar piping kan initiëren.

In tegenstelling tot de klassieke BOI-benadering wordt geen enkele
doorsnede beschouwd, maar een **hiërarchische combinatie van
faalmechanismen en scenario’s**.

Faalmechanismen en scenario’s
-------------------------------------

Per uittredepunt worden meerdere faalmechanismen beschouwd, waaronder:

- uplift
- heave
- piping

Voor elk faalmechanisme worden meerdere hydraulische en geotechnische
scenario’s doorgerekend.
Per scenario wordt een faalkans bepaald, inclusief bijbehorende
FORM-resultaten (β en α).

De faalkans per scenario wordt bepaald met Importance Sampling rondom
de FORM-design points.

Combinatie tot faalkans per uittredepunt
---------------------------------------------- 

De faalkans van een uittredepunt volgt uit de combinatie van alle
scenario’s die tot falen kunnen leiden:

.. math::

   P_{f,\mathrm{uittrede}} =
   \sum_{i=1}^{N_\mathrm{scen}}
   P(\mathrm{scenario}_i)\, P_f(\mathrm{scenario}_i)

De bijbehorende betrouwbaarheidsindex volgt uit:

.. math::

   \beta_{\mathrm{uittrede}} = -\Phi^{-1}(P_{f,\mathrm{uittrede}})

De richting van falen (α-vector) wordt **niet gemiddeld**, maar
overgenomen uit het **meest ongunstige scenario**, omdat dit scenario
dominant is voor het optreden van falen.