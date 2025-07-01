import pandas as pd
from geoprob_pipe.input_data.vak import VakCollection
from geoprob_pipe.input_data.ondergrond_scenario import OndergrondScenarioCollection
from geoprob_pipe.input_data.uittredepunt import UittredepuntCollection
from geoprob_pipe.input_data.overschrijdingsfrequentielijn import OverschrijdingsfrequentielijnCollection
from geoprob_pipe.classes.workspace import Workspace
from geoprob_pipe.helper_functions.data_validation import checks_input_parameters, checks_overview_parameters
import logging


logger = logging.getLogger("geoprob_pipe_logger")


class InputData:
    """ Subclass to group input data of vakken, uittredepunten and ondergrondscenarios. Data is retrieved from the input
    Excel-file. """

    def __init__(self, workspace: Workspace):

        # Read overview data of parameters from input Excel file (includes e.g. upper and lower bounds, type of
        # distribution, etc.) and carry out checks
        self.df_overview_parameters = pd.read_excel(
            workspace.path_input_excel, sheet_name="Overzicht_parameters",
            index_col=0, header=0).rename(columns=lambda x: x.strip())
        checks_overview_parameters(self.df_overview_parameters)

        # Collections
        self.vakken = VakCollection(workspace=workspace, df_overview_parameters=self.df_overview_parameters)
        self.uittredepunten = UittredepuntCollection(
            workspace=workspace, vak_collection=self.vakken, df_overview_parameters=self.df_overview_parameters)
        self.ondergrondscenarios = OndergrondScenarioCollection(
            workspace=workspace, vak_collection=self.vakken, df_overview_parameters=self.df_overview_parameters)
        checks_input_parameters(
            self.df_overview_parameters, self.vakken.df, self.uittredepunten.df, self.ondergrondscenarios.df)
        logger.info(f"Parameter data successfully loaded from `{workspace.path_input_excel.name}`")

        # HRD-data
        self.overschrijdingsfrequentielijnen = OverschrijdingsfrequentielijnCollection(
            path_hrd=workspace.path_hrd, uittredepunt_collection=self.uittredepunten)
        logger.info(f"HRD .sqlite file successfully loaded from `{workspace.path_hrd.name}`")
