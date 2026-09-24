from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import geoprob_pipe.cmd_app.validation.validate_expanded_table as module


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"mean": 12.5}, 12.5),
        ("{'mean': 12.5}", 12.5),
        ("{'distribution_type': 'normal'}", np.nan),
        (None, None),
    ],
)
def test_get_mean(value, expected) -> None:
    result = module.get_mean(value)

    if isinstance(expected, float) and np.isnan(expected):
        assert np.isnan(result)
    else:
        assert result == expected


def test_check_match_marks_missing_source_value_as_none() -> None:
    df_check = pd.DataFrame(index=[0, 1])
    df_compare = pd.DataFrame(
        {
            "mean": [10.0, 10.0],
            "mean_traject": [10.0, np.nan],
        }
    )

    result = module._check_match(df_check, df_compare, "mean_traject")

    assert result.loc[0, "match_traject"] is True
    assert pd.isna(result.loc[1, "match_traject"])


@pytest.mark.parametrize(
    "row, expected",
    [
        ([None, True, None], False),
        ([None, True, False], True),
        ([False, None, True, None], False),
    ],
)
def test_has_priority_error(row, expected) -> None:
    assert module.has_priority_error(row) is expected


def _tables() -> SimpleNamespace:
    return SimpleNamespace(
        df_parameter_invoer=pd.DataFrame(
            {
                "parameter": ["param"],
                "scope": ["traject"],
                "scope_referentie": [1],
                "ondergrondscenario_naam": ["scenario"],
                "mean": [10.0],
                "minimum": [None],
                "maximum": [None],
                "fragility_values_ref": [None],
                "bronnen": [None],
                "opmerking": [None],
            }
        ),
        df_gis_join_parameter_invoer=pd.DataFrame(
            {
                "parameter": ["other_param"],
                "scope_referentie": [2],
                "ondergrondscenario_naam": ["scenario"],
                "mean": [20.0],
            }
        ),
    )


def _expanded(mean: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "parameter_name": ["param"],
            "vak_id": [1],
            "uittredepunt_id": [1],
            "ondergrondscenario_naam": ["scenario"],
            "parameter_input": [{"mean": mean}],
        }
    )


def test_validate_expand_tables_does_not_export_valid_rows(tmp_path) -> None:
    module.validate_expand_tables(
        tables=_tables(),
        geopackage_filepath=str(tmp_path / "project.gpkg"),
        df_expanded=_expanded(10.0),
    )

    assert not list(tmp_path.glob("exports/*/parameter_input_process/*.xlsx"))


def test_validate_expand_tables_exports_mismatch(tmp_path) -> None:
    module.validate_expand_tables(
        tables=_tables(),
        geopackage_filepath=str(tmp_path / "project.gpkg"),
        df_expanded=_expanded(11.0),
    )

    exports = list(tmp_path.glob("exports/*/parameter_input_process/*.xlsx"))
    assert [path.name for path in exports] == ["validation_expanded_table_input.xlsx"]
