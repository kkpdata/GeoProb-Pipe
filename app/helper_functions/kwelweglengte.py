import pandas as pd
import numpy as np

# tijdelijk dataframe voor testen, kolommen komen overeen met input vanuit sheet
df_input_kwelweg_test = pd.read_excel(r'V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx', sheet_name='input_kwelweglengte')

# tijdelijk dataframe voor testen, input komt eigenlijk uit functie statistiek
df_input_kwelweg_doorlatendheid_param = pd.read_excel(r'V:\dr_Waterkeringen\08. Kennis\02. Probabilitische rekenen - werkmap\GeoProb-Pipe\testcase 20-4 STPH\Test_bestand_geoprob_pipe.xlsx', sheet_name='TEMP_doorl_param')

#  tijdelijke merge voor testen
df_input_kwelweglengte = df_input_kwelweg_test.merge(df_input_kwelweg_doorlatendheid_param, left_index=True, right_index=True)

# toevoegen -> test voor input (enkel floats)

df_input_kwelweglengte['Kwelweglengte'] = df_input_kwelweglengte['Uittredepunt'] - df_input_kwelweglengte['Begin voorland']
df_input_kwelweglengte['Lengte voorland'] = df_input_kwelweglengte['Buitenteen'] - df_input_kwelweglengte['Begin voorland']
df_input_kwelweglengte['Breedte dijklichaam'] = df_input_kwelweglengte['Uittredepunt'] - df_input_kwelweglengte['Buitenteen']
df_input_kwelweglengte['Breedte achterland'] = df_input_kwelweglengte['Uittredepunt'] - df_input_kwelweglengte['Binnenteen']
df_input_kwelweglengte['c1 [dagen]'] = 100 * df_input_kwelweglengte['d [m]']
df_input_kwelweglengte['lambda_1 [m]'] = (df_input_kwelweglengte['k [m/dag]'] * df_input_kwelweglengte['D [m]'] * df_input_kwelweglengte['c1 [dagen]']) ** 0.5
df_input_kwelweglengte['fictief voorland'] = df_input_kwelweglengte['lambda_1 [m]']  * np.tanh(df_input_kwelweglengte['Lengte voorland']/df_input_kwelweglengte['lambda_1 [m]'])
df_input_kwelweglengte['Fictieve kwelweglengte'] = df_input_kwelweglengte['Breedte dijklichaam'] + df_input_kwelweglengte['fictief voorland']

def kwelweglengte_func():
    return df_input_kwelweglengte



