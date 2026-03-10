from geoprob_pipe.results.assemblage.functions import combine_series
from geoprob_pipe.results.assemblage.functions import window_collect
from geoprob_pipe.results.assemblage.functions import scaled_collect
from geoprob_pipe.results.assemblage.objects import UittredepuntElement


def test_combine():
    """Test combining very small floats.
    """
    pfs = [1.123e-17, 3.78e-15, 6.7e-15]
    sum_pf, max_pf = combine_series(pfs)
    assert sum_pf == 1.049123e-14
    assert max_pf == 6.7e-15


def test_window():
    """Test window on selecting max in window and combining.
    """
    list_dsn = [
        UittredepuntElement(m_value=11, a=0.9, converged=True, pf=1e-12),
        UittredepuntElement(m_value=12, a=0.9, converged=True, pf=2e-13),
        UittredepuntElement(m_value=20, a=0.9, converged=True, pf=7.5e-13),
        UittredepuntElement(m_value=30, a=0.9, converged=True, pf=3e-14)
    ]
    sum_pf, max_pf, elements = window_collect(
        window_size=10, point_list=list_dsn,
        m_van=0, m_tot=40
        )
    assert sum_pf == 1.78e-12
    assert max_pf == 1e-12
    assert elements.__len__() == 4
    assert elements[0].kans_dsn.pf == 0.0


def test_scaled():
    """Test scaled on taking max in cluster and combining.
    """
    list_dsn = [
        UittredepuntElement(m_value=11, a=0.9, converged=True, pf=1e-12),
        UittredepuntElement(m_value=12, a=0.9, converged=True, pf=2e-13),
        UittredepuntElement(m_value=20, a=0.9, converged=True, pf=7.5e-13),
        UittredepuntElement(m_value=30, a=0.9, converged=True, pf=3e-14)
    ]
    sum_pf, max_pf, elements = scaled_collect(
        dL=200, point_list=list_dsn,
        m_van=0, m_tot=50
        )
    assert sum_pf == 1.78e-12
    assert max_pf == 1e-12
    assert elements.__len__() == 3
