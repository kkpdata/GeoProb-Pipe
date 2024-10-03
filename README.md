# GeoProb-Pipe
Tool voor het parallel uitvoeren van probabilistische pipingberekeningen.

# Contactpersonen
- Laura van der Doef, L.vanderDoef@wshd.nl
- Martijn Kriebel, mkriebel@avecodebondt.nl

# Installatie
Deze tool in ontwikkeld met Python versie 3.12.5.
Installatie van de dependencies:
```python
pip install -r requirements.txt
```

# Software
Deze tool is ontwikkeld met onderstaande software versies:
- Probabilistic Toolkit (PTK) 2023.2.343.0

Andere versies werken mogelijk ook maar zijn niet gecheckt.

De tool gaat ervan uit dat de Probabilistic Toolkit lokaal geïnstalleerd is in `C:\Program Files (x86)\Deltares\Probabilistic Toolkit`. Als dit niet het geval is kunnen de paden naar de PTK server en executable gewijzigd worden in `app/classes/toolkit_settings.py`.
<br>

# Opbouw tool
<span style="background-color:green">#TODO: UPDATEN</span>

Voor het gebruik van de tool zijn twee onderdelen van belang.
## Script `app/main_fragility_curve.py`
Hoofdscript waarmee de tool wordt uitgevoerd. Bovenaan het script is een "user input section" aangegeven. Hierin geeft de gebruiker een aantal parameters op:
  - Waterstandsstatistieken (`MU` en `SIGMA`). Deze worden bepaald met het standalone script `helper_functions/fit_extreme_value_dist_water_level.py`. Let op: dit script is overgenomen van Deltares en niet geïntegreerd in deze tool. De gebruiker is zelf verantwoordelijk voor het afleiden van de juiste mu en sigma met `fit_extreme_value_dist_water_level.py` en deze over te nemen in `main_fragility_curve.py`.
  - Modus van de tool:
    - Gebruik resultaten van reeds uitgevoerde PTK berekeningen (`USE_EXISTING_TKX_RESULTS=True`), zie voorbeeld 1.
    - Starten van nieuwe PTK-bestanden (`USE_EXISTING_TKX_RESULTS=False`), zie voorbeeld 2.
  - Pad naar de "workspace" map (`PATH_WORKSPACE`). Zie volgende punt.
## Map `workspaces`
Bevat alle input, output en tijdelijke rekenbestanden per doorgerekende locatie worden opgeslagen. Indien nieuwe prob. macrostabiliteitssommen worden uitgevoerd, dient een nieuwe map aangemaakt te worden (bijv. `workspaces/sommen_locatie_X`). Na het uitvoeren van de tool bestaat deze map uit de volgende mappen:
  - `input` bestaat uit:
    -  D-Stability (.stix) bestanden waarvoor de berekeningen zijn/worden uitgevoerd. Elk .stix bestand betreft een andere buitenwaterstand; overige aspecten van de .stix moeten identiek aan elkaar zijn.
    -  Template PTK (.tkx) bestand die als basis voor de PTK-berekeningen gebruikt wordt. Hierin moeten de variabelen gedefinieerd zijn die onderzocht worden incl. statistische parameters. Daarnaast bevat dit bestand de probabilistische rekeninstellingen. Let op: alleen nodig als nieuwe berekeningen worden uitgevoerd (dus `USE_EXISTING_TKX_RESULTS=True`). 
  - `output` bestaat uit:
    - PTK (.tkx) bestanden met resultaten van de probabilistische berekeningen.
    - Excel-bestand met resultaten die zijn uitgelezen uit de .tkx bestanden.
  - `_work_dir`: bevat tussentijdse rekenbestanden. Moet leeg zijn voordat de tool uitgevoerd kan worden om problemen met oude rekenbestanden te voorkomen.

# Voorbeelden
<span style="background-color:green">#TODO: UPDATEN</span>
## Voorbeeld 1: bestaande PTK-resultaten
Zie `workspaces/_example_precalculated_output`

Gebruikt resultaten van reeds uitgevoerde PTK berekeningen (dus `USE_EXISTING_TKX_RESULTS=True`)
  - Benodigd:
    - Distributieparameters (`MU` en `SIGMA`) voor de waterstandsstatistiek. Deze worden opgegeven in `app/main_fragility_curve.py`
    - D-Stability (.stix) bestanden die zijn gebruikt in de eerder uitgevoerde .tkx bestanden. Deze worden geplaatst in `workspaces/_example_precalculated_output/input`
    - PTK (.tkx) bestanden die eerder zijn uitgevoerd. Deze worden geplaatst in `workspaces/_example_precalculated_output/output`
  - Resultaat:
    - Afbeeldingen worden weergeven in de IDE waarin de tool uitgevoerd wordt.
    - Een Excel-bestand wordt gegenereerd in `workspaces/_example_precalculated_output/output`

## Voorbeeld 2: nieuwe PTK-sommen
Zie `workspaces/_example_new_calculations`

Start nieuwe probabilistische PTK-berekeningen (dus `USE_EXISTING_TKX_RESULTS=False`):
  - Benodigd:
    - Distributieparameters (`MU` en `SIGMA`) voor de waterstandsstatistiek. Deze worden opgegeven in `app/main_fragility_curve.py`
    - D-Stability (.stix) bestanden in `workspaces/_example_new_calculations/input`
    - Template PTK (.tkx) bestand in `workspaces/_example_new_calculations/input`
  - Resultaat:
    - Afbeeldingen worden weergeven in de IDE waarin de tool uitgevoerd wordt.
    - .tkx bestanden met resultaten van de probabilistische berekeningen worden opgeslagen in `workspaces/_example_precalculated_output/output`
    - Een Excel-bestand wordt gegenereerd in `workspaces/_example_precalculated_output/output`

# Eisen aan input
<span style="background-color:green">#TODO: UPDATEN</span>
## D-Stability rekenbestanden (.stix):
- Bevatten alle data die normaliter ook aanwezig moet zijn voor een reguliere D-Stability berekening. Dit betekent dat in het .stix bestand o.a. geometrie, grondlagen, belastingen, instellingen m.b.t. rekenmodel (Bishop/UpliftVan/Spencer, zoekgebieden etc.) gedefiniëerd zijn.
- Moeten geldig zijn (validity/integrity). Om hier zeker van te zijn wordt aangeraden om de .stix bestanden eerst deterministisch met D-Stability te laten doorrekenen.
- Mogen maar één scenario bevatten. Dit scenario mag wel uit verschillende stages bestaan. Het scenario bevat één calculation.
- Om de buitenwaterstand te bepalen kijkt de tool naar het eerste (meest linkse) punt op de freatische waterlijn. Zorg ervoor dat deze de juiste waarde heeft.

**Tip:** de (template) .tkx neemt parameterverdelingen over die al in de input .stix zijn gedefinieerd. Er wordt daarom aanbevolen om stochasten (voor zover mogelijk) al in de input .stix te definiëren voordat de template .tkx wordt opgezet. Dit scheelt werk en zorgt voor eenduidige input.
<br>

## PTK template rekenbestand (.tkx):
- Moet geldig zijn (validity/integrity). Om hier zeker van te zijn wordt aangeraden om  het .tkx bestand te openen met de PTK om te kijken of er validation errors zijn en of de variabelen (en bijbehorende verdelingen) correct zijn gedefinieerd.
- Model type moet "Application" zijn, met als application "D-Stability".

# Disclaimer
Het gebruik van deze tool gebeurt volledig op eigen risico. Door deze tool te gebruiken, accepteert de gebruiker volledige verantwoordelijkheid. De ontwikkelaars kunnen geen garanties geven over de werking, nauwkeurigheid of volledigheid van de tool, en kunnen op geen enkele manier verantwoordelijk worden gehouden voor eventuele fouten, schade, of verliezen die voortvloeien uit het gebruik van deze software.