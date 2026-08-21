from geoprob_pipe.workflow.base_objects import Step
from typing import List, Type
from geoprob_pipe.workflow.questions.import_hrd import QuestionImportHRD


steps: List[Type[Step]] = [

    # HRD
    QuestionImportHRD,
    # QuestionDirectoryPathHydraNLDatabase,
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
