#from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from file_system import FileSystem

# #FIXME @Oscar evt. ParameterCollection gebruiken als parent class voor Uittredepunten, Scenarios en Vakken

filepath_test = r'C:\Users\oscop\Documents\GeoProb-Pipe\input_data'

class ParameterCollection:
     """Contains input parameters from Excel"""
    
     def __init__(self, filepath: Path) -> None:
        self.files = FileSystem.find_files_in_dir(filepath, "xlsx")
        if not self.files:
            raise FileNotFoundError(f"Geen files gevonden in de opgegeven map")
        
        self.inputexcel = self.files[0]
        #FIXME er moet nog een check komen of file inderdaad inputtabel.xlsx is.
        # if self.inputexcel != filepath + r'\inputtabel.xlsx':
        #     raise FileNotFoundError(f"1 Excelfile in map zetten met naam inputtabel.xlsx, niet meer niet minder")
        
        self.df_vakken = pd.read_excel(self.inputexcel, sheet_name="Vakken")
        self.df_uittredepunten = pd.read_excel(self.inputexcel, sheet_name="Uittredepunten")
        self.df_scenarios = pd.read_excel(self.inputexcel, sheet_name="Scenarios")   
        #evt -> df met algemene parameters

parameters = ParameterCollection(filepath_test)

class Vak:
    def __init__(self, parameters: ParameterCollection):
        self.parameters = parameters
      
    def add_uittredepunt(self, locatie, row: pd.DataFrame):
        #FIXME raise error bij inlezen input.xlsx als kolomnamen niet kloppen/missen
        punt = Uittredepunt(self, locatie)
        for ...
            setattr(punt, kolomnaam, row[kolomnaam])
        self.uittredepunten.append(punt)
        return punt

    def __repr__(self):
        return f"Vak(naam={self.naam}, c1={self.c1}, c3={self.c3})"

# class Uittredepunt:
#     def __init__(self, vak: Vak, locatie):
#         self.vak = vak
#         self.locatie = locatie
#         self.c1 = vak.c1
#         self.c3 = vak.c3

#     def __repr__(self):
#         return f"Uittredepunt(locatie={self.locatie}, c1={self.c1}, c3={self.c3}, vak={self.vak.naam})"


# v1 = Vak("Dijkvak 12", c1=0.25, c3=1.73)

# df = ...read_excel..

# for i, row in df.itterrows():
#     v1.add_uittredepunt(row["locatie"], row)


# class OndergrondScenario:
#     def __init__(self, vak: Vak, naam, scenario):
#         self.vak = vak
#         self.naam = naam
#         self.scenario = scenario

#     def __repr__(self):
#         return f"OndergrondScenario(naam={self.naam}, scenario={self.scenario})"

# class Vak:
#     def __init__(self, naam, c1, c3):
#         self.naam = naam
#         self.c1 = c1
#         self.c3 = c3
#         self.uittredepunten = []

#     def add_uittredepunt(self, locatie):
#         punt = Uittredepunt(self, locatie)
#         self.uittredepunten.append(punt)
#         return punt

#     def __repr__(self):
#         return f"Vak(naam={self.naam}, c1={self.c1}, c3={self.c3})"


# class Uittredepunt:
#     def __init__(self, vak: Vak, locatie):
#         self.vak = vak
#         self.locatie = locatie
#         self.c1 = vak.c1
#         self.c3 = vak.c3

#     def __repr__(self):
#         return f"Uittredepunt(locatie={self.locatie}, c1={self.c1}, c3={self.c3}, vak={self.vak.naam})"


# v1 = Vak("Dijkvak 12", c1=0.25, c3=1.73)
 
# u1 = v1.add_uittredepunt("km 2.3")
# u2 = v1.add_uittredepunt("km 3.0")


# class Vakken():
#     def __init__(self, filepath: Path) -> None:
#         self.df = pd.read_excel(filepath, sheet_name="Vak")
        
#         @dataclass
#         class Params:
#             UittredepuntID: int
#             X_uitrede: float
#             Y_uitrede: float
#             Uitredelocatie: str
#             Mvalue: float
#             VakID: int
#             Vaknaam: str
#             DIST_L_GEOM: float
#             DIST_BUT: float
#             DIST_BIT: float
#             WBN: float
#             HydraLocatieID: str
#             Bodemhoogte: float
#             Polderpei: float
#             Top_zand_lokaal: float
#             Top_zand_regionaal: float
#             Top_klei_lokaal: float            
        
#         self.params = Params(self.df)




        
# class Uittredepunten:
#     ...
    
# class Scenarios:
#     ...