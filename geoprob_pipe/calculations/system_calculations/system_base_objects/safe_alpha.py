import numpy as np
from probabilistic_library.reliability import Alpha
from geoprob_pipe.calculations.system_calculations.system_base_objects.safe_stochast import SafeStochast


def _py(x):
    """robust cast for numpy types -> Python scalars"""
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    return x


class SafeAlpha(Alpha):
    """
    Safe subclass of probabilistic_library.reliability.Alpha
    that can exist in two modes:
      - Live: full C-backed interface as used in probabilistic_library
      - Rebuild: pure Python cached data which no longer contains any
        c pointers. Cannot be used to rerun the calculation but can be
        used in the rest of the code.

    The original Alpha class in probabilistic library cannot be pickeld.
    Therefore this class functions a "rebuild" clone without any c pointers.
    """

    def __init__(self, *args, _rebuild=False, **kwargs):
        if not _rebuild:
            super().__init__(*args, **kwargs)
            self._rebuild = False
        else:
            # Do not call base __init__ to avoid creating a C object
            self._id = 0
            self._rebuild = True
            self._variable_cached = None

        # Always define all attributes for compatibility
        self._variable = getattr(self, "_variable", None)
        self._known_variables = getattr(self, "_known_variables", None)
        self._identifier_cached = getattr(self, "_identifier_cached", None)
        self._alpha_cached = getattr(self, "_alpha_cached", None)
        self._alpha_correlated_cached = getattr(self, "_alpha_correlated_cached", None)
        self._influence_factor_cached = getattr(self, "_influence_factor_cached", None)
        self._index_cached = getattr(self, "_index_cached", None)
        self._u_cached = getattr(self, "_u_cached", None)
        self._x_cached = getattr(self, "_x_cached", None)

    # -------------------------------------------------------------------------
    # EXPORT TO PURE PYTHON DICT
    # -------------------------------------------------------------------------
    def to_plain(self) -> dict:
        """Export this Alpha as a pure Python dict (safe for pickling)."""

        var = getattr(self, "variable", None)
        if var is not None:
            dist_value = getattr(getattr(var, "distribution", None), "value", None)
            variable_data = {
                "name": getattr(var, "name", None),
                "distribution": dist_value,  # <- ensure primitive
                "mean": _py(getattr(var, "mean", None)),
                "minimum": _py(getattr(var, "minimum", None)),
                "maximum": _py(getattr(var, "maximum", None)),
                "deviation": _py(getattr(var, "deviation", None)),
                "variation": _py(getattr(var, "variation", None)),
            }
        else:
            variable_data = None

        return {
            "identifier": getattr(self, "identifier", None),
            "alpha": _py(getattr(self, "alpha", None)),
            "alpha_correlated": _py(getattr(self, "alpha_correlated", None)),
            "influence_factor": _py(getattr(self, "influence_factor", None)),
            "index": _py(getattr(self, "index", None)),
            "u": _py(getattr(self, "u", None)),
            "x": _py(getattr(self, "x", None)),
            "variable": variable_data,
        }

    # -------------------------------------------------------------------------
    # REBUILD FROM PLAIN DICT
    # -------------------------------------------------------------------------
    @classmethod
    def from_plain(cls, data: dict):
        """Rebuild a SafeAlpha from a pure Python dict."""
        a = cls(_rebuild=True)
        a._id = 0
        a._identifier_cached = data.get("identifier")
        a._alpha_cached = data.get("alpha")
        a._alpha_correlated_cached = data.get("alpha_correlated")
        a._influence_factor_cached = data.get("influence_factor")
        a._index_cached = data.get("index")
        a._u_cached = data.get("u")
        a._x_cached = data.get("x")
        variable_data = data.get("variable")
        if isinstance(variable_data, dict):
            a._variable_cached = SafeStochast.from_plain(variable_data)
        elif isinstance(variable_data, str):
            a._variable_cached = SafeStochast(name=variable_data)
        else:
            a._variable_cached = None

        return a

    # -------------------------------------------------------------------------
    # SAFE PROPERTY OVERRIDES
    # -------------------------------------------------------------------------
    @property
    def identifier(self):
        if getattr(self, "_rebuild", False):
            return self._identifier_cached
        return super().identifier

    @property
    def alpha(self):
        if getattr(self, "_rebuild", False):
            return self._alpha_cached
        return super().alpha

    @property
    def alpha_correlated(self):
        if getattr(self, "_rebuild", False):
            return self._alpha_correlated_cached
        return super().alpha_correlated

    @property
    def influence_factor(self):
        if getattr(self, "_rebuild", False):
            return self._influence_factor_cached
        return super().influence_factor

    @property
    def index(self):
        if getattr(self, "_rebuild", False):
            return self._index_cached
        return super().index

    @property
    def u(self):
        if getattr(self, "_rebuild", False):
            return self._u_cached
        return super().u

    @property
    def x(self):
        if getattr(self, "_rebuild", False):
            return self._x_cached
        return super().x

    @property
    def variable(self):
        if getattr(self, "_rebuild", False):
            # Always return a SafeStochast
            var = getattr(self, "_variable_cached", None)
            if isinstance(var, SafeStochast):
                return var
            elif isinstance(var, dict):
                return SafeStochast.from_plain(var)
            elif isinstance(var, str):
                return SafeStochast(name=var)
            elif var is None:
                return SafeStochast()  # default stub
            else:
                # fallback: already a Stochast-like object
                return var
        # Live mode
        return super().variable

    def __repr__(self):
        tag = "[rehydrated]" if getattr(self, "_rebuild", False) else "[live]"
        return (
            f"<SafeAlpha {tag} id={getattr(self, '_id', None)} "
            f"alpha={self.alpha} influence={self.influence_factor}>"
        )
