![Coverage](./readme_images/coverage.svg)

# GeoProb-Pipe
Applicatie voor het uitvoeren van probabilistische piping berekeningen. De applicatie maakt gebruik van de probabilistische 
bibliotheek van Deltares. Deze bibliotheek stuurt onder de motorkap de PTK-tool aan. 


# Contactpersonen

Het GeoProb-Pipe-team bestaat uit de volgende personen

- Sander Kapinga, S.Kapinga@wsrl.nl
- Laura van der Doef, L.vanderDoef@wshd.nl
- Chris Pitzalis, ontwikkelaar, C.Pitzalis@wsrl.nl
- Vincent Jilesen, ontwikkelaar, V.Jilesen@wshd.nl


# Installatie
Op termijn wordt GeoProb-Pipe beschikbaar gesteld middels de Python Package Index (https://pypi.org) voor een eenvoudige 
installatie via `pip install geoprob-pipe`. Voor nu is de installatie als volgt:

 - Kloon de repository middels `git clone repo_weblink`.
 - Maak een virtuele Python environment aan. Deze applicatie is ontwikkeld met Python versie 3.12. 
 - Installeer alle dependencies middels `pip install -r requirements.txt`. 


# Quickstart
Start de applicatie als volgt

- Vanuit de gekloonde repository met het commando `python -m geoprob_pipe.questionnaire.cmd startup_geoprob_pipe`.
- Wanneer de package/wheel geïnstalleerd is met het commando `geoprob-pipe`. 


# Mee ontwikkelen
Wil je bijdragen aan de ontwikkeling van GeoProb-Pipe? Dat kan! :)

Maak een nieuwe branch aan vanuit `dev`, ga coden en wanneer je klaar bent, maak een pull en review request aan. Zorg 
er voor dat de unit tests werken en dat je PEP8 als code stijl hanteert. Bij vragen, neem contact op met één van de 
ontwikkelaars. Voor PEP8, de IDE PyCharm heeft deze out of the box ingesteld. PyCharm is daarom de geadviseerde IDE.  


# Documentatie
De documentatie genereer je middels het commando `sphinx-build -M html docs\ docs\_build`. Je vindt de 
documentatie daarna terug in de map `GeoProb-Pipe\docs\_build\html\index.html`. Dit bestand opent in de browser. Tip: 
voeg de documentatie toe aan je favorieten van de browser. 



# Disclaimer
Het gebruik van deze applicatie gebeurt volledig op eigen risico. Door deze applicatie te gebruiken, accepteert de 
gebruiker volledige verantwoordelijkheid. Het GeoProb-Pipe-team kan geen garanties geven over de werking, 
nauwkeurigheid of volledigheid van de applicatie, en kan op geen enkele manier verantwoordelijk worden gehouden voor 
eventuele fouten, schade, of verliezen die voortvloeien uit het gebruik van deze software.
