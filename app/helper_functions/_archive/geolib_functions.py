from pathlib import Path

from geolib.models.dstability import DStabilityModel
from geolib.models.dstability.internal import PersistableHeadLine, Waternet


def find_phreatic_line(waternet: Waternet) -> PersistableHeadLine:
    """Find the phreatic line in a given Waternet object.

    Args:
        waternet (Waternet): Waternet object to search in

    Raises:
        ValueError: raised if no phreatic line could be found

    Returns:
        PersistableHeadLine: phreatic line
    """
    for headline in waternet.HeadLines:
        if headline.Id == waternet.PhreaticLineId:
            return headline
    raise ValueError("No phreatic line found")


def find_phreatic_waterlevel_from_waternet(waternet: Waternet) -> float:
    """Find the phreatic waterlevel in a Waternet object. Assumptions:
    - The waterlevel is given by the first (most left) point of the phreatic line

    Args:
        waternet (Waternet): Waternet object

    Returns:
        float: phreatic waterlevel (=Z-coordinate of leftmost point of the phreatic line)
    """
    phreatic_line = find_phreatic_line(waternet)
    return min(phreatic_line.Points, key=lambda point: point.X).Z  # type: ignore


def get_waterlevels(stix_model: DStabilityModel) -> float:
    """Get phreatic waterlevel of a D-Stability model. Assumptions:
    1) The waterlevel is given by the first (most left) point of the phreatic line
    2) If the model contains multiple waterlevels (because of multiple stages), the highest waterlevel found from these
       waternets is assumed to be the waterlevel of interest.

    Args:
        stix_model (DStabilityModel): D-Stability model

    Returns:
        float: waterlevel (=Z-coordinate of leftmost point of the phreatic line)
    """
    return max(find_phreatic_waterlevel_from_waternet(waternet) for waternet in stix_model.datastructure.waternets)


def parse_stix(path_stix: Path) -> DStabilityModel:
    """Parse .stix file to a DStabilityModel object

    Args:
        path_stix (Path): path to .stix file

    Returns:
        DStabilityModel: D-Stability model object
    """
    dm = DStabilityModel()
    dm.parse(path_stix)
    return dm


def check_stix_validity_integrity_structure(dm: DStabilityModel) -> None:
    """Check validity/integrity of the D-Stability model

    Args:
        dm (DStabilityModel): D-Stability model object

    Raises:
        ValueError: raised if the D-Stability model is invalid
    """
    if not dm.is_valid:
        raise ValueError(
            f"D-Stability file {Path(dm.datastructure.projectinfo.Path).name} is not valid. Check this .stix in D-Stability to see what's wrong."  # type: ignore
        )


def check_stix_one_scenario(dm: DStabilityModel) -> None:
    """Check whether the D-Stability model has only one scenario

    Args:
        dm (DStabilityModel): D-Stability model object

    Raises:
        ValueError: raised if the D-Stability model contains more than one scenario
    """
    if not len(dm.scenarios) == 1:
        raise ValueError(
            f"D-Stability file {Path(dm.datastructure.projectinfo.Path).name} contains multiple scenarios, but only 1 scenario is allowed."  # type: ignore
        )


def check_stix_one_calculation(dm: DStabilityModel) -> None:
    """Check whether the D-Stability model has only one calculation

    Args:
        dm (DStabilityModel): D-Stability model object

    Raises:
        ValueError: raised if the D-Stability model contains more than one calculation
    """
    if not len(dm.datastructure.calculationsettings) == 1:
        raise ValueError(
            f"D-Stability file {Path(dm.datastructure.projectinfo.Path).name} contains multiple calculations, but only 1 calculation is allowed."  # type: ignore
        )
