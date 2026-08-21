from geoprob_pipe.workflow.base_objects import Step
from typing import List, Type
from geoprob_pipe.workflow.questions import QuestionImportHRD, QuestionDirHydraNLDatabase


steps: List[Type[Step]] = [

    # HRD
    QuestionImportHRD,
    QuestionDirHydraNLDatabase,
    # ActionImportHRDFromHydraNLDatabase,
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
