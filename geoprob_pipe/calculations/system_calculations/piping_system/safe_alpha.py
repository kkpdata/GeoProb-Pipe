from probabilistic_library import interface
from probabilistic_library.reliability import Alpha


class SafeAlpha(Alpha):
    """
    Safe subclass of probabilistic_library.reliability.Alpha
    that can exist in two modes:
      - Live: full C-backed interface
      - Rehydrated: pure Python cached data (no C calls)
    """

    def __init__(self, *args, _rehydrated=False, **kwargs):
        if not _rehydrated:
            super().__init__(*args, **kwargs)
            self._rehydrated = False
        else:
            # Do not call base __init__ to avoid creating a C object
            self._id = 0
            self._rehydrated = True
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
    # SAFE DESTRUCTOR
    # -------------------------------------------------------------------------
    def __del__(self):
        try:
            if getattr(self, "_rehydrated", False):
                return
            _id = getattr(self, "_id", 0)
            if _id:
                interface.Destroy(_id)
                self._id = 0
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # EXPORT TO PURE PYTHON DICT
    # -------------------------------------------------------------------------
    def to_plain(self) -> dict:
        """Export this Alpha as a pure Python dict (safe for pickling)."""
        data = {}
        try:
            data["identifier"] = getattr(self, "identifier", None)
            data["alpha"] = getattr(self, "alpha", None)
            data["alpha_correlated"] = getattr(self, "alpha_correlated", None)
            data["influence_factor"] = getattr(self, "influence_factor", None)
            data["index"] = getattr(self, "index", None)
            data["u"] = getattr(self, "u", None)
            data["x"] = getattr(self, "x", None)
        except Exception:
            pass

        # Variable: store minimal info to link back later
        try:
            variable = getattr(self, "variable", None)
            if variable is not None:
                data["variable"] = getattr(variable, "name", str(variable))
        except Exception:
            data["variable"] = None

        return data

    # -------------------------------------------------------------------------
    # REHYDRATION FROM PLAIN DICT
    # -------------------------------------------------------------------------
    @classmethod
    def from_plain(cls, data: dict):
        """Rebuild a SafeAlpha from a pure Python dict (no C calls)."""
        a = cls(_rehydrated=True)
        a._id = 0
        a._identifier_cached = data.get("identifier")
        a._alpha_cached = data.get("alpha")
        a._alpha_correlated_cached = data.get("alpha_correlated")
        a._influence_factor_cached = data.get("influence_factor")
        a._index_cached = data.get("index")
        a._u_cached = data.get("u")
        a._x_cached = data.get("x")
        a._variable_cached = data.get("variable")
        return a

    # -------------------------------------------------------------------------
    # SAFE PROPERTY OVERRIDES
    # -------------------------------------------------------------------------
    @property
    def identifier(self):
        if getattr(self, "_rehydrated", False):
            return self._identifier_cached
        return super().identifier

    @property
    def alpha(self):
        if getattr(self, "_rehydrated", False):
            return self._alpha_cached
        return super().alpha

    @property
    def alpha_correlated(self):
        if getattr(self, "_rehydrated", False):
            return self._alpha_correlated_cached
        return super().alpha_correlated

    @property
    def influence_factor(self):
        if getattr(self, "_rehydrated", False):
            return self._influence_factor_cached
        return super().influence_factor

    @property
    def index(self):
        if getattr(self, "_rehydrated", False):
            return self._index_cached
        return super().index

    @property
    def u(self):
        if getattr(self, "_rehydrated", False):
            return self._u_cached
        return super().u

    @property
    def x(self):
        if getattr(self, "_rehydrated", False):
            return self._x_cached
        return super().x

    @property
    def variable(self):
        if getattr(self, "_rehydrated", False):
            return self._variable_cached
        return super().variable

    def __repr__(self):
        tag = "[rehydrated]" if getattr(self, "_rehydrated", False) else "[live]"
        return (
            f"<SafeAlpha {tag} id={getattr(self, '_id', None)} "
            f"alpha={self.alpha} influence={self.influence_factor}>"
        )
