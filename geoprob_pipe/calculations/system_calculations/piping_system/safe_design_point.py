from probabilistic_library import DesignPoint, interface
from geoprob_pipe.calculations.system_calculations.piping_system.safe_alpha import SafeAlpha


class SafeDesignPoint(DesignPoint):
    """
    A DesignPoint subclass that is fully interchangeable with the original,
    but can also exist as a "rehydrated" (pure Python) clone with no C pointers.
    """

    # ---------------------------------------------------------------------
    # INITIALISATION
    # ---------------------------------------------------------------------
    def __init__(self, *args, _rehydrated=False, **kwargs):
        # Normal DesignPoint initialisation if not rehydrated
        if not _rehydrated:
            super().__init__(*args, **kwargs)
            self._rehydrated = False
        else:
            # Create a shell without calling DesignPoint.__init__
            # because we don't want to allocate a C object.
            self._id = 0
            self._rehydrated = True

        # Ensure all internal attributes exist for interchangeability
        self._alphas = getattr(self, "_alphas", None)
        self._contributing_design_points = getattr(self, "_contributing_design_points", None)
        self._messages = getattr(self, "_messages", None)
        self._realizations = getattr(self, "_realizations", None)
        self._known_variables = getattr(self, "_known_variables", None)
        self._known_design_points = getattr(self, "_known_design_points", None)

        # Cache fields for rehydrated clones
        self._identifier_cached = getattr(self, "_identifier_cached", None)
        self._reliability_index_cached = getattr(self, "_reliability_index_cached", None)
        self._probability_failure_cached = getattr(self, "_probability_failure_cached", None)
        self._convergence_cached = getattr(self, "_convergence_cached", None)
        self._is_converged_cached = getattr(self, "_is_converged_cached", None)
        self._total_directions_cached = getattr(self, "_total_directions_cached", None)
        self._total_iterations_cached = getattr(self, "_total_iterations_cached", None)
        self._total_model_runs_cached = getattr(self, "_total_model_runs_cached", None)
        self._alphas_cached = getattr(self, "_alphas_cached", [])
        self._messages_cached = getattr(self, "_messages_cached", [])
        self._contributing_design_points_cached = getattr(
            self, "_contributing_design_points_cached", []
        )

    # ---------------------------------------------------------------------
    # SAFE DESTRUCTOR
    # ---------------------------------------------------------------------
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

    # ---------------------------------------------------------------------
    # EXPORT TO PLAIN DICT
    # ---------------------------------------------------------------------
    def to_plain(self, include_nested=False, max_depth=1) -> dict:
        """Export this SafeDesignPoint and its alphas as pure Python data."""
        data = {}
        try:
            data["identifier"] = self.identifier
            data["reliability_index"] = self.reliability_index
            data["probability_failure"] = self.probability_failure
            data["convergence"] = self.convergence
            data["is_converged"] = self.is_converged
            data["total_directions"] = self.total_directions
            data["total_iterations"] = self.total_iterations
            data["total_model_runs"] = self.total_model_runs
        except Exception:
            pass

        # ----------------------------------------------------------------------
        # ✅ Export detailed alpha info (including variable distribution)
        # ----------------------------------------------------------------------
        data["alphas"] = []
        try:
            for a in getattr(self, "alphas", []):
                data["alphas"].append(a.to_plain())
        except Exception:
            pass

        # ----------------------------------------------------------------------
        # Messages (optional diagnostics)
        # ----------------------------------------------------------------------
        data["messages"] = []
        try:
            for m in getattr(self, "messages", []):
                data["messages"].append(str(m))
        except Exception:
            pass

        if include_nested and max_depth > 0:
            nested = []
            try:
                for dp in getattr(self, "contributing_design_points", []):
                    if isinstance(dp, DesignPoint):
                        nested.append(
                            SafeDesignPoint(dp._id).to_plain(
                                include_nested=True, max_depth=max_depth - 1
                            )
                        )
                data["contributing_design_points"] = nested
            except Exception:
                pass

        return data

    # ---------------------------------------------------------------------
    # REHYDRATION FROM DICT
    # ---------------------------------------------------------------------
    @classmethod
    def from_plain(cls, data: dict):
        dp = cls(_rehydrated=True)
        dp._identifier_cached = data.get("identifier")
        dp._reliability_index_cached = data.get("reliability_index")
        dp._probability_failure_cached = data.get("probability_failure")
        dp._convergence_cached = data.get("convergence")
        dp._is_converged_cached = data.get("is_converged")
        dp._total_directions_cached = data.get("total_directions")
        dp._total_iterations_cached = data.get("total_iterations")
        dp._total_model_runs_cached = data.get("total_model_runs")
        raw_alphas = data.get("alphas", [])
        dp._alphas_cached = [SafeAlpha.from_plain(a) for a in raw_alphas]
        dp._messages_cached = data.get("messages", [])
        dp._contributing_design_points_cached = [
            cls.from_plain(c) for c in data.get("contributing_design_points", [])
        ]
        return dp

    # ---------------------------------------------------------------------
    # PROPERTY OVERRIDES (cached when rehydrated)
    # ---------------------------------------------------------------------
    def _cached_or(self, attr, fallback):
        if getattr(self, "_rehydrated", False):
            return getattr(self, attr, None)
        return fallback

    @property
    def is_converged(self):
        if getattr(self, "_rehydrated", False):
            return bool(getattr(self, "_is_converged_cached", False))
        return super().is_converged

    @property
    def reliability_index(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_reliability_index_cached", None)
        return super().reliability_index

    @property
    def probability_failure(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_probability_failure_cached", None)
        return super().probability_failure

    @property
    def convergence(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_convergence_cached", None)
        return super().convergence

    @property
    def total_directions(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_total_directions_cached", None)
        return super().total_directions

    @property
    def total_iterations(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_total_iterations_cached", None)
        return super().total_iterations

    @property
    def total_model_runs(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_total_model_runs_cached", None)
        return super().total_model_runs

    @property
    def identifier(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_identifier_cached", None)
        return super().identifier

    @property
    def alphas(self):
        if getattr(self, "_rehydrated", False):
            # already plain dicts or lightweight items as you stored them
            return getattr(self, "_alphas_cached", [])
        return super().alphas

    @property
    def messages(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_messages_cached", [])
        return super().messages

    @property
    def contributing_design_points(self):
        if getattr(self, "_rehydrated", False):
            return getattr(self, "_contributing_design_points_cached", [])
        return super().contributing_design_points

    def __repr__(self):
        tag = "[rehydrated]" if getattr(self, "_rehydrated", False) else "[live]"
        return (
            f"<SafeDesignPoint {tag} id={getattr(self, '_id', None)} "
            f"name={self.identifier} β={self.reliability_index} Pf={self.probability_failure}>"
        )
