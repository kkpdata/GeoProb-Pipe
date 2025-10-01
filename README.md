![Coverage](./readme_images/coverage.svg)

# GeoProb-Pipe
Applicatie voor het uitvoeren van probabilistische piping berekeningen. De tool maakt gebruik van de probabilistische 
bibliotheek van Deltares. Deze bibliotheek stuurt onder de motorkap de PTK-tool aan. 


# Contactpersonen
- Sander Kapinga, S.Kapinga@wsrl.nl
- Laura van der Doef, L.vanderDoef@wshd.nl
- Chris Pitzalis, C.Pitzalis@wsrl.nl


# Installatie
Op termijn wordt GeoProb-Pipe beschikbaar gesteld middels de Python Package Index (https://pypi.org) voor een eenvoudige 
installatie via `pip install geoprob-pipe`. Voor nu is de installatie als volgt:

 - Kloon de repository middels `git clone repo_weblink`.
 - Maak een virtuele Python environment aan. Deze tool is ontwikkeld met Python versie 3.12. 
 - Installeer alle dependencies middels `pip install -r requirements.txt`. 


# Quickstart
Tool wordt gestart door `main_piping.py` te runnen.

Benodigdheden:
- Het `geoprob_pipe.ini` in de root-map. Vul hierin het pad naar de workspace in.
- Een projectmap in "workspaces" (bijv. .../workspaces/my_project).
- In de projectmap een submap "input" (.../workspaces/my_project/input).
- De input-map de volgende bestanden:
  - input.xlsx (gebruik hiervoor het meegeleverde template input.xlsx).
  - De hydraulische database bestanden (.sqlite-bestanden).


# Mee ontwikkelen
Wil je bijdragen aan de ontwikkeling van GeoProb-Pipe? Dat kan! 

Maak een nieuwe branch aan vanuit `dev`, ga coden en wanneer je klaar bent, maak een pull en review request aan. Zorg 
er voor dat de unit tests werken en dat je PEP8 als code stijl hanteert. Bij vragen, neem contact op met één van de 
ontwikkelaars. Voor PEP8, de IDE PyCharm heeft deze out of the box ingesteld. PyCharm is daarom de geadviseerde IDE.  


# Documentatie
De documentatie kan worden gegeneerd middels het commando `sphinx-build -M html docs\ docs\_build`. Je vindt de 
documentatie daarna terug in de map `GeoProb-Pipe\docs\_build\html\index.html`. Dit bestand opent in de browser. Tip: 
voeg de documentatie toe aan je favorieten van de browser. 



# Disclaimer
Het gebruik van deze tool gebeurt volledig op eigen risico. Door deze tool te gebruiken, accepteert de gebruiker 
volledige verantwoordelijkheid. De ontwikkelaars kunnen geen garanties geven over de werking, nauwkeurigheid of 
volledigheid van de tool, en kunnen op geen enkele manier verantwoordelijk worden gehouden voor eventuele fouten, 
schade, of verliezen die voortvloeien uit het gebruik van deze software.


# TODO's
Hieronder staat een overzicht van de TODO’s, voorzien van tags die aangeven: wanneer ze relevant zijn, hoe belangrijk 
ze zijn, en wat de omvang van de TODO betreft. De lijst is gesorteerd op urgentie en prioriteit (must/should), zodat 
snel duidelijk is waar de code aangescherpt of uitgebreid kan worden. In de tabel staat alleen een korte omschrijving; 
bij de TODO in de code zelf is vaak een uitgebreidere toelichting te vinden. 


### Nu van belang

<!-- START_TODO_TABLE_NU -->
| Belang | Formaat | Beschrijving | Bestand | Regel |
| -- | -- | -- | -- | -- |
| could | middel | Uitvoeren van system calculations ombouwen naar Threads. | /calculations/system_calculations/piping_system/build_and_run.py | 25 | 
| must | klein | Voor export df_beta_limit_states, kolommen filteren? | /results/__init__.py | 67 | 
| must | klein | Eigenlijk hoofdletter N_dsn. Maar ipv afkorting naam gebruiken? | /misc/traject_normering.py | 76 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | /visualizations/graphs/betrouwbaarheidsindex.py | 92 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | /visualizations/graphs/betrouwbaarheidsindex.py | 115 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | /visualizations/graphs/betrouwbaarheidsindex.py | 116 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | /visualizations/graphs/betrouwbaarheidsindex.py | 191 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | /visualizations/graphs/betrouwbaarheidsindex.py | 214 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | /visualizations/graphs/betrouwbaarheidsindex.py | 215 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 49 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 72 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 73 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 152 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 175 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 176 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 261 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 283 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | /visualizations/graphs/betrouwbaarheidsindex_oud.py | 284 | 
| must | middel | Optie toevoegen dat ParallelSystemReliabilityCalculation ook deterministisch word uitgerekend | /calculations/system_calculations/piping_system/test_calculation.py | 53 | 
| must | middel | Assert toevoegen die piping resultaat unit test | /calculations/system_calculations/piping_system/test_calculation.py | 55 | 
| should | groot | Zou goed zijn om in GeoProb-Pipe voorbeelden op te nemen die tonen dat de applicatie klopt. | /calculations/test_prob_lib_vs_openturns.py | 1 | 
| should | klein | Sommige resultaten zijn niet converged. Wat doen we daarmee? | /results/__init__.py | 70 | 
| should | klein | I.p.v. dict maak gebruik van Distributie-objecten. Minder fout gevoelig. | /calculations/system_calculations/system_base_objects/parallel_system_reliability_calculation.py | 71 | 
| should | klein | Feedback aan gebruiker dat er validation messages zijn. | /calculations/system_calculations/system_base_objects/parallel_system_reliability_calculation.py | 137 | 
| should | klein | Onderstaande class is momenteel het Python Notebook voorbeeld van Deltares. Omzetten. | /calculations/system_calculations/piping_system/reliability_calculation.py | 10 | 

<!-- END_TODO_TABLE_NU --> 

































### Op een later moment van belang
<details>
  <summary>Bekijk de tabel</summary>

  <br>

<!-- START_TODO_TABLE_LATER -->
| Belang | Formaat | Beschrijving | Bestand | Regel |
| -- | -- | -- | -- | -- |
| could | groot | Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze. | /app_object.py | 30 | 
| could | groot | Add functionality to read existing results (without running prob. calculations again) | /utils/workspace.py | 23 | 
| could | klein | Bespreken of we de physical values willen afronden? Af wellicht afrondden in de export. | /results/df_alphas_influence_factors_and_physical_values.py | 108 | 
| could | klein | Elk sub-object heeft een export_dir-method. Kan dit handiger? | /results/__init__.py | 49 | 
| could | middel | De bovenstaande assertion triggert. Maar dat is fout. | /calculations/test_prob_lib_vs_openturns.py | 132 | 
| must | klein | Check dat een LineString-laag wordt opgegeven. | /pre_processing/spatial_layers/dijktraject.py | 90 | 
| nice | middel | Visualiseer physical design point value in hfreq-plot ter bewustzijn. | /visualizations/graphs/hfreq.py | 20 | 
| should | klein | D zit ook in kD_wvp. Dat is dubbelop. | /calculations/system_calculations/piping_system/limit_state_functions.py | 9 | 
| should | klein | Waarom zijn alle vaste parameters toegevoegd? Zoals zwaartekracht g. Global maken? | /calculations/system_calculations/piping_system/limit_state_functions.py | 75 | 
| should | klein | Nadenken hoe we binnen een half uur een quick scan piping kunnen uitvoeren met het object. | /calculations/system_calculations/piping_system/test_calculation.py | 4 | 
| should | klein | Is het echt nodig om een 'FileSystem'-object te maken? Deze functies bestaan al toch? | /utils/file_system.py | 9 | 
| should | middel | Het zou goed zijn om voor dit simpele systeem ook betas te kunnen reproduceren. | /calculations/test_prob_lib_vs_openturns.py | 175 | 
| should | middel | Visualiseer WBN waterstand in hfreq-plot ter bewustzijn. | /visualizations/graphs/hfreq.py | 19 | 
| should | middel | We vragen nu filepath, we kunnen daarnaast de optie geven voor normtrajecten direct. | /pre_processing/spatial_layers/dijktraject.py | 22 | 
| should | middel | Should validate if AHN grid fully overlaps area | /pre_processing/spatial_layers/ahn.py | 13 | 

<!-- END_TODO_TABLE_LATER --> 































</details>



