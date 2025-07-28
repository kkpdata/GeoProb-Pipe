![Coverage](./readme_images/coverage.svg)

# GeoProb-Pipe
Tool voor het parallel uitvoeren van probabilistische pipingberekeningen. De tool maakt gebruik van de probabilistische bibliotheek van Deltares.

# Ontwikkeling
Deze repository is in ontwikkeling. In `dev_kernel_structure` worden de functionaliteiten ontwikkeld om de structuur van de database en de rekenkernel inclusief testen op te nemen. In `main` staan de functionaliteiten voor data invoer/uitvoer, de koppeling met de probabilitistische bibliotheek en het uitvoeren van de probabilistische som.

# Contactpersonen
- Sander Kapinga, S.Kapinga@wsrl.nl
- Laura van der Doef, L.vanderDoef@wshd.nl
- Martijn Kriebel, mkriebel@avecodebondt.nl

# Installatie
Deze tool in ontwikkeld met Python versie 3.12.5.
Installatie van de dependencies:
- Conda (aanbevolen, environment incl. correcte Python versie wordt automatisch aangemaakt):
  - Methode 1: via Anaconda Navigator. Ga naar "environments" en importeer het .yml bestand.
  - Methode 2: via  Anaconda Prompt
    ```console
    # Install dependencies
    conda env create -f environment.yml

    # Activate env
    conda activate GeoProb-Pipe
    ```
- Pip (gebruiker moet zelf de environment aanmaken met juiste Python versie):
  ```console
  # Create environnment (note: use aforementioned supported Python version)
  python -m venv GeoProb-Pipe

  # Activate env
  GeoProb-Pipe/bin/activate

  # Install dependencies
  pip install -r requirements.txt
  ```

# Ontwikkeling

- Pip (gebruiker moet zelf de environment aanmaken met juiste Python versie):
  ```console
  # Create environnment (note: use aforementioned supported Python version)
  python -m venv GeoProb-Pipe

  # Activate env
  GeoProb-Pipe/bin/activate

  # Install dependencies
  pip install -r requirements.txt
  pip install -r dev-requirements.txt
  ```

# Documentatie
De beschrijving van de rekenkernel is opgenomen in de documentatie. De documentatie kan worden gegeneerd door:

windows:
```console
sphinx-build -M html docs\ docs\_build
```

# Quickstart
Tool wordt gestart door `main_piping.py` te runnen.

Benodigdheden:
- Een projectmap in "workspaces" (bijv. .../workspaces/my_project) met daarin een submap "input" (.../workspaces/my_project/input)
- De input-map bevat:
  - input.xlsx (gebruik hiervoor het meegeleverde template input.xlsx)
  - Unzipped HRD .sqlite (hydraulische database). Deze mag zowel in de input-map als in een submap staan.


# Disclaimer
Het gebruik van deze tool gebeurt volledig op eigen risico. Door deze tool te gebruiken, accepteert de gebruiker volledige verantwoordelijkheid. De ontwikkelaars kunnen geen garanties geven over de werking, nauwkeurigheid of volledigheid van de tool, en kunnen op geen enkele manier verantwoordelijk worden gehouden voor eventuele fouten, schade, of verliezen die voortvloeien uit het gebruik van deze software.


# TODO's
Hieronder staat een overzicht van de TODO’s, voorzien van tags die aangeven: wanneer ze relevant zijn, hoe belangrijk 
ze zijn, en wat de omvang van de TODO betreft. De lijst is gesorteerd op urgentie en prioriteit (must/should), zodat 
snel duidelijk is waar de code aangescherpt of uitgebreid kan worden. In de tabel staat alleen een korte omschrijving; 
bij de TODO in de code zelf is vaak een uitgebreidere toelichting te vinden. 


### Nu van belang

<!-- START_TODO_TABLE_NU -->
| Belang | Formaat | Beschrijving | Bestand | Regel |
| -- | -- | -- | -- | -- |
| must | klein | Exporteer df met resultaten per limit state. | \app_object.py | 90 | 
| must | klein | Exporteer df met resultaten per combinatie. | \app_object.py | 96 | 
| must | klein | Unit test uitbreiden/toevoegen met buitenwaterstand als distributie. | \calculations\system_calculations\piping_system\test_calculation.py | 56 | 
| must | klein | In het Openturns voorbeeld heeft deze een derde parameter met waarde 10. Waarvoor? | \calculations\system_calculations\piping_system\test_calculation.py | 108 | 
| must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. | \graphs\combined\betrouwbaarheidsindex.py | 48 | 
| must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. | \graphs\combined\betrouwbaarheidsindex.py | 71 | 
| must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. | \graphs\combined\betrouwbaarheidsindex.py | 72 | 
| must | klein | naam toevoegen van afkorting | \misc\traject_normering.py | 11 | 
| must | middel | Visualiseer de limit state resultaten. | \app_object.py | 216 | 
| must | middel | Visualiseer de combined resultaten. | \app_object.py | 225 | 
| must | middel | Visualiseer een vergelijking tussen de combined en de limit state resultaten. | \app_object.py | 228 | 
| must | middel | Optie toevoegen dat ParallelSystemReliabilityCalculation ook deterministisch word uitgerekend | \calculations\system_calculations\piping_system\test_calculation.py | 194 | 
| must | middel | Assert toevoegen die piping resultaat unit test | \calculations\system_calculations\piping_system\test_calculation.py | 196 | 
| should | klein | Onderstaande class is momenteel het Python Notebook voorbeeld van Deltares. Omzetten. | \calculations\system_calculations\piping_system\reliability_calculation.py | 10 | 
| should | klein | I.p.v. dict maak gebruik van Distributie-objecten. Minder fout gevoelig. | \calculations\system_calculations\system_base_objects\parallel_system_reliability_calculation.py | 71 | 
| should | klein | Feedback aan gebruiker dat er validation messages zijn. | \calculations\system_calculations\system_base_objects\parallel_system_reliability_calculation.py | 138 | 
| should | middel | Uitvoeren van system calculations ombouwen naar Threads | \app_object.py | 84 | 
| should | middel | Implement Thread Executor for this. | \app_object.py | 189 | 
| should | middel | Implementeer ThreadPoolExecutor voor 'run combined'. | \calculations\combined.py | 46 | 

<!-- END_TODO_TABLE_NU --> 








### Op een later moment van belang
<details>
  <summary>Bekijk de tabel</summary>

  <br>

<!-- START_TODO_TABLE_LATER -->
| Belang | Formaat | Beschrijving | Bestand | Regel |
| -- | -- | -- | -- | -- |
| could | groot | Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze. | \app_object.py | 57 | 
| could | groot | Add functionality to read existing results (without running prob. calculations again) | \classes\workspace.py | 25 | 
| could | middel | De bovenstaande assertion triggert. Maar dat is fout. | \calculations\test_prob_lib_vs_openturns.py | 131 | 
| must | middel | Exporteer df met resultaten per uittredepunt. | \app_object.py | 109 | 
| must | middel | Exporteer df met resultaten per vak. | \app_object.py | 110 | 
| should | klein | Bespreken wat we met resultaten doen die niet 'converged' zijn. | \app_object.py | 214 | 
| should | klein | D zit ook in kD_wvp. Dat is dubbelop. | \calculations\system_calculations\piping_system\limit_state_functions.py | 11 | 
| should | klein | Nadenken hoe we binnen een half uur een quick scan piping kunnen uitvoeren met het object. | \calculations\system_calculations\piping_system\test_calculation.py | 4 | 
| should | middel | Alpha en/of influence_factors exporteren in een aparte Excel. | \app_object.py | 212 | 
| should | middel | Het zou goed zijn om voor dit simpele systeem ook betas te kunnen reproduceren. | \calculations\test_prob_lib_vs_openturns.py | 174 | 
| should | middel | Gebruiksvriendelijkheid vergroten voor andere reliability_methods. | \classes\reliability_calculation.py | 116 | 

<!-- END_TODO_TABLE_LATER --> 






</details>



