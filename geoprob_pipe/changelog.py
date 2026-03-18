
CHANGELOG = {
    "1.4.2":
        "Documentation update.",
    "1.4.1":
        "Documentation update.",
    "1.4.0":
        "Implementatie van een nieuwe versie van de System Calculation. Van af nu worden er drie scenario analyses "
        "uitgevoerd: een Combine Project en Reliability project over een gezamenlijke grenstoestandsfuncties voor "
        "uplift, heave en piping, en een Reliability Project over de grenstoestandsfuncties apart. Vervolgens wordt "
        "op basis van een stroomschema (zie documentatie) de meest optimale berekening geselecteerd.",
    "1.3.21":
        "Start met validatie van invoer Excel-sheets. Bewuste keuze voor SQL-queries (leesbaarheid), in plaats van "
        "pandera.",
    "1.3.20":
        "New feature: Methode geïmplementeerd om input_parameters.xlsx te valideren op invoer. Methode is voor nu "
        "een start. Validatie moet nog toegevoegd worden.",
    "1.3.19":
        "(a) Hotfix: Nieuwe versie probabilistic_library stond geen Beta van de overschrijdingsfrequentielijn toe "
        "van hoger dan 8.0. Hydra-NL lijkt tot en met 8.0 te gaan, waardoor het laatste punt soms net boven de 8.0 "
        "valt. Er wordt nu afgekapt in GeoProb-Pipe. "
        "(b) New feature: Indien een berekening faalt, wordt er nu een log opgeslagen van deze berekening. Applicatie "
        "blijft ook doordraaien, i.p.v. crash."
        "(c) Hotfix: Validatie issue bij importeren nieuwe Input-Excel opgelost.",
    "1.3.1":
        "Hotfix. Visualisatie en export issues. Geen issue aan berekeningen zelf. 1e issue: Foute beta waarden in de "
        "hover van de betrouwbaarheidsindex.html. 2e issue: De df_limit_states werd geëxporteerd als df_scenarios.",
    "1.3.0":
        "Probabilistic Library nu toegevoegd als 'setup dependency' nadat Deltares deze heeft vrijgegeven op PyPI. "
        "Eveneens Chrome uitgefaseerd als software requirement. Daardoor zijn beiden geen handmatige software "
        "requirements meer.",
    "1.2.0":
        "Implementatie van parallel rekenen en het inspecteren van een enkele berekening.",
    "1.1.0":
        "Implementatie van een eerste versie van het vergelijken van twee verschillende GeoProb-Pipe bestanden.",
    "1.0.0":
        "Implementatie GeoPackage als data (in- en uitvoer) bestand én implementatie van keuze in geohydrologische "
        "modellen.",
    "0.1.0":
        "Toevoegen features na interne gebruikerssessie WSRL 2025-08-11: (a) geopackage-export met resultaten, "
        "(b) Excel-export met physical values, alphas en invloedsfactoren, (c) Excel-export met resultaat per vak, "
        "(d) Excel-export met validatie berichten en (e) physical values in grafiek waterstandssfrequentielijn.",
    "0.0.15":
        "Eerste vrijgave van wheel installatie-bestand.",
}
