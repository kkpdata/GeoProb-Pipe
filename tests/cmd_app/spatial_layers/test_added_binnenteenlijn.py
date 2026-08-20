from unittest.mock import Mock

import geoprob_pipe.cmd_app.spatial_layers.binnenteenlijn as module


def test_added_binnenteenlijn_already_included(
    monkeypatch,
    capsys,
) -> None:
    app_settings = Mock()
    app_settings.geopackage_filepath = "dummy.gpkg"

    monkeypatch.setattr(
        module.fiona,
        "listlayers",
        Mock(return_value=[
            "trajectlijn",
            "binnenteenlijn",
            "vakindeling",
        ]),
    )

    request_mock = Mock()
    monkeypatch.setattr(
        module,
        "request_binnenteenlijn_filepath",
        request_mock,
    )

    result = module.added_binnenteenlijn(app_settings)

    assert result is True

    request_mock.assert_not_called()

    captured = capsys.readouterr()
    assert "Binnenteenlijn al toegevoegd" in captured.out
    
def test_added_binnenteenlijn_not_yet_included(
    monkeypatch,
):
    app_settings = Mock()
    app_settings.geopackage_filepath = "dummy.gpkg"

    monkeypatch.setattr(
        module.fiona,
        "listlayers",
        Mock(return_value=[
            "trajectlijn",
            "vakindeling",
        ]),
    )

    request_mock = Mock()
    monkeypatch.setattr(
        module,
        "request_binnenteenlijn_filepath",
        request_mock,
    )

    result: bool = module.added_binnenteenlijn(app_settings)

    assert result is True

    request_mock.assert_called_once_with(
        app_settings=app_settings
    )