import pytest

import geoprob_pipe.results.assemblage.functions as functions
import geoprob_pipe.results.assemblage.objects as objects


@pytest.fixture
def uittredepunten() -> list[objects.UittredepuntElement]:
    return [
        objects.UittredepuntElement(
            m_value=11,
            a=0.9,
            converged=True,
            pf=1e-12,
            flow_chart_number=11,
            advise="-",
        ),
        objects.UittredepuntElement(
            m_value=12,
            a=0.9,
            converged=True,
            pf=2e-13,
            flow_chart_number=11,
            advise="-",
        ),
        objects.UittredepuntElement(
            m_value=20,
            a=0.9,
            converged=True,
            pf=7.5e-13,
            flow_chart_number=11,
            advise="-",
        ),
        objects.UittredepuntElement(
            m_value=30,
            a=0.9,
            converged=True,
            pf=3e-14,
            flow_chart_number=11,
            advise="-",
        ),
    ]


def test_combine_series_with_small_probabilities() -> None:
    """Check addition of very small probabilities"""

    # Arrange
    pfs: list[float] = [1.123e-17, 3.78e-15, 6.7e-15]

    # Act
    sum_pf: float
    max_pf: float
    sum_pf, max_pf = functions.combine_series(pfs)

    # Assert
    assert sum_pf == pytest.approx(1.049123e-14)
    assert max_pf == pytest.approx(6.7e-15)


def test_combine_series_empty_list() -> None:
    """Assert correct return on input of empty list."""
    # Arrange
    pfs: list[float] = []

    # Act
    sum_pf: float
    max_pf: float
    sum_pf, max_pf = functions.combine_series(pfs)

    # Assert
    assert sum_pf == 0.0
    assert max_pf == 0.0


@pytest.mark.parametrize(
    "L, a, dL, expected",
    [
        (100.0, 0.5, 20.0, 2.5),  # larger than 1
        (10.0, 0.5, 20.0, 1.0),  # minimum = 1
        (20.0, 1.0, 20.0, 1.0),  # exact 1
        (200.0, 0.8, 40.0, 4.0),  # normal case
    ],
)
def test_bepaal_N_vak(L: float, a: float, dL: float, expected: float) -> None:
    """Controleer correcte calculation of N_vak."""
    result = functions.bepaal_N_vak(L=L, a=a, dL=dL)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "a",
    [-0.1, -1.0, -100.0],
)
def test_bepaal_N_vak_raises_for_negative_a(a: float) -> None:
    """Assert that a negative value of a raise a ValueError"""
    with pytest.raises(ValueError, match="a moet groter zijn dan 0"):
        functions.bepaal_N_vak(L=100.0, a=a, dL=20.0)


@pytest.mark.parametrize(
    "L, dL",
    [
        (-1.0, 20.0),
        (100.0, -20.0),
        (-1.0, -20.0),
    ],
)
def test_bepaal_N_vak_raises_for_negative_lengths(L: float, dL: float) -> None:
    """Assert that negative values for L and dL raise a ValueError."""
    with pytest.raises(
        ValueError,
        match="De lengte L en dL moeten groter zijn dan 0",
    ):
        functions.bepaal_N_vak(L=L, a=0.5, dL=dL)


def test_window_collect_returns_expected_values(uittredepunten) -> None:
    """Check selection inside windows and combined probability."""

    # Act
    sum_pf: float
    max_pf: float
    elements: list[objects.WindowElement]
    sum_pf, max_pf, elements = functions.window_collect(
        window_size=10,
        point_list=uittredepunten,
        m_van=0,
        m_tot=40,
    )

    # Assert
    assert sum_pf == pytest.approx(1.78e-12)
    assert max_pf == pytest.approx(1e-12)
    assert len(elements) == 4
    assert elements[0].kans_dsn.pf == pytest.approx(0.0)


def test_window_collect_empty_list() -> None:
    # Act
    sum_pf: float
    max_pf: float
    elements: list[objects.WindowElement]
    sum_pf, max_pf, elements = functions.window_collect(
        window_size=10,
        point_list=[],
        m_van=0,
        m_tot=50,
    )

    # Assert
    assert sum_pf == 0.0
    assert max_pf == 0.0
    assert len(elements) == 0


def test_scaled_collect_returns_expected_values(uittredepunten) -> None:
    """Check clustering, scale factor en combined probability."""

    # Act
    sum_pf: float
    max_pf: float
    elements: list[objects.WindowElement]
    sum_pf, max_pf, elements = functions.scaled_collect(
        dL=200,
        point_list=uittredepunten,
        m_van=0,
        m_tot=50,
    )

    # Assert
    assert sum_pf == pytest.approx(1.78e-12)
    assert max_pf == pytest.approx(1e-12)
    assert len(elements) == 3


def test_scaled_collect_empty_list() -> None:
    # Act
    sum_pf: float
    max_pf: float
    elements: list[objects.WindowElement]
    sum_pf, max_pf, elements = functions.scaled_collect(
        dL=200,
        point_list=[],
        m_van=0,
        m_tot=50,
    )

    # Assert
    assert sum_pf == 0.0
    assert max_pf == 0.0
    assert len(elements) == 0