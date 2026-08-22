from geoprob_pipe.workflow.base_objects import Step
from typing import List, Type
from geoprob_pipe.workflow.questions import QuestionImportHRD, QuestionDirHydraNLDatabase
from geoprob_pipe.workflow.actions import ActionImportHRDLocationsFromHydraNLDatabase

steps: List[Type[Step]] = [

    # HRD
    QuestionImportHRD,
    QuestionDirHydraNLDatabase,
    ActionImportHRDLocationsFromHydraNLDatabase,
    # ActionImportTrajectParametersFromHydraNLDatabase,
    # QuestionFilePathGeoProbPipeFileWithHRD,
    # ActionImportHRDFromOtherGeoProbPipeFile,
    # ActionImportTrajectParametersFromOtherGeoProbPipeFile,

    # Traject parameters
    # QuestionTrajectID,
    # QuestionSignaleringswaarde,
    # QuestionOndergrens,
    # QuestionW,
    # QuestionIsBovenrivierengebied,

    # Uittredepunten
    # QuestionPathToUittredepuntenGISFile,
    # ActionImportUittredepuntenGISFile,
]
