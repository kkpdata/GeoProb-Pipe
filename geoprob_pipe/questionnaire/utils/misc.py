from importlib.metadata import version, PackageNotFoundError


def get_geoprob_pipe_version_number() -> str:
    geoprob_pipe_version_number = "DEV"
    try: geoprob_pipe_version_number = version('geoprob_pipe')
    except PackageNotFoundError: pass
    return geoprob_pipe_version_number
