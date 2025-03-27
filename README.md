# GeoProb-Pipe
Tool voor het parallel uitvoeren van probabilistische pipingberekeningen.

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
- Pip (gebruiker moet zelf de environemnt aanmaken met juiste Python versie):
  ```console
  # Create environnment (note: use aforementioned supported Python version)
  python -m venv GeoProb-Pipe

  # Activate env
  GeoProb-Pipe/bin/activate

  # Install dependencies
  pip install -r requirements.txt
  ```

# Disclaimer
Het gebruik van deze tool gebeurt volledig op eigen risico. Door deze tool te gebruiken, accepteert de gebruiker volledige verantwoordelijkheid. De ontwikkelaars kunnen geen garanties geven over de werking, nauwkeurigheid of volledigheid van de tool, en kunnen op geen enkele manier verantwoordelijk worden gehouden voor eventuele fouten, schade, of verliezen die voortvloeien uit het gebruik van deze software.