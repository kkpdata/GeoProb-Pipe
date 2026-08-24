import pytest

from geoprob_pipe.cmd_app.cmd import ApplicationSettings


@pytest.fixture
def app_settings(tmp_path) -> ApplicationSettings:
    settings = ApplicationSettings()
    
    settings.workspace_dir = str(tmp_path)
    settings.geopackage_filename = "dummy.gpkg"
    
    return settings