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
Hieronder een overzicht van de TODO's die getagd zijn met wanneer ze van belang zijn, het belang, en het formaat van de 
TODO. Ze zijn gesorteerd op welke nu van belang zijn en welke een must of should zijn. Zodoende kan snel bekeken worden 
waar de code aangescherpt of uitgebreid kan worden. 


<!-- START_TODO_TABLE -->
| Bestand | Regel | Wanneer | Belang | Formaat | Beschrijving |
| -- | -- | -- | -- | -- | -- |
| \app_object.py | 75 | nu | must | klein | Exporteer df met resultaten per limit state. |
| \app_object.py | 79 | nu | must | klein | Exporteer df met resultaten per combinatie. |
| \calculations\system_calculations\piping_system\test_calculation.py | 53 | nu | must | klein | Unit test uitbreiden/toevoegen met buitenwaterstand als distributie. |
| \calculations\system_calculations\piping_system\test_calculation.py | 105 | nu | must | klein | In het Openturns voorbeeld heeft deze een derde parameter met waarde 10. Waarvoor? |
| \graphs\combined\betrouwbaarheidsindex.py | 48 | nu | must | klein | Pas dijkpaal codering op x-as toe. Heb op dit moment niet deze gekoppeld aan de measure. |
| \graphs\combined\betrouwbaarheidsindex.py | 71 | nu | must | klein | Dit zijn niet de officiële categoriekleuren. Aanpassen. |
| \graphs\combined\betrouwbaarheidsindex.py | 72 | nu | must | klein | De fills lijken een kleine overlap te hebben waardoor het lijkt alsof er een border is. |
| \misc\traject_normering.py | 11 | nu | must | klein | naam toevoegen van afkorting |
| \app_object.py | 199 | nu | must | middel | Visualiseer de limit state resultaten. |
| \app_object.py | 208 | nu | must | middel | Visualiseer de combined resultaten. |
| \app_object.py | 211 | nu | must | middel | Visualiseer een vergelijking tussen de combined en de limit state resultaten. |
| \calculations\system_calculations\parallel_system_reliability_calculation.py | 117 | nu | must | middel | Valideer of alle benodigde keys zijn gegeven. |
| \calculations\system_calculations\piping_system\test_calculation.py | 191 | nu | must | middel | Optie toevoegen dat ParallelSystemReliabilityCalculation ook deterministisch word uitgerekend |
| \calculations\system_calculations\piping_system\test_calculation.py | 193 | nu | must | middel | Assert toevoegen die piping resultaat unit test |
| \calculations\system_calculations\parallel_system_reliability_calculation.py | 56 | nu | should | klein | I.p.v. dict maak gebruik van Distributie-objecten. Minder fout gevoelig. |
| \calculations\system_calculations\piping_system\reliability_calculation.py | 10 | nu | should | klein | Onderstaande class is momenteel het Python Notebook voorbeeld van Deltares. Omzetten. |
| \app_object.py | 172 | nu | should | middel | Implement Thread Executor for this. |
| \calculations\combined.py | 46 | nu | should | middel | Implementeer ThreadPoolExecutor voor 'run combined'. |
| \app_object.py | 50 | later | could | groot | Gebruiker optie geven OpenTurns of Prob-library te kiezen? Dus engine keuze. |
| \classes\workspace.py | 25 | later | could | groot | Add functionality to read existing results (without running prob. calculations again) |
| \calculations\test_prob_lib_vs_openturns.py | 131 | later | could | middel | De bovenstaande assertion triggert. Maar dat is fout. |
| \app_object.py | 92 | later | must | middel | Exporteer df met resultaten per uittredepunt. |
| \app_object.py | 93 | later | must | middel | Exporteer df met resultaten per vak. |
| \app_object.py | 197 | later | should | klein | Bespreken wat we met resultaten doen die niet 'converged' zijn. |
| \calculations\system_calculations\piping_system\limit_state_functions.py | 19 | later | should | klein | D zit ook in kD_wvp. Dat is dubbelop. |
| \app_object.py | 195 | later | should | middel | Alpha en/of influence_factors exporteren in een aparte Excel. |
| \calculations\test_prob_lib_vs_openturns.py | 174 | later | should | middel | Het zou goed zijn om voor dit simpele systeem ook betas te kunnen reproduceren. |
| \calculations\system_calculations\parallel_system_reliability_calculation.py | 71 | later | should | middel | Validation message wanneer de hoogste limit state beta significant lager is dan het systeem |
| \classes\reliability_calculation.py | 116 | later | should | middel | Gebruiksvriendelijkheid vergroten voor andere reliability_methods. |

<!-- END_TODO_TABLE --> 
