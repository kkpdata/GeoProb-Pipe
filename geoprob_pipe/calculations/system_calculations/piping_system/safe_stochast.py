class SafeStochast:
    """Pure-Python replacement for probabilistic_library.Stochast."""
    def __init__(self, name=None, distribution=None, value=None, **kwargs):
        self.name = name or "<unknown>"
        # Always create a lightweight object for .distribution.value
        self.distribution = type("DistributionType", (), {"value": distribution or "<unknown>"})()
        self._extra = kwargs

    def __repr__(self):
        return f"<SafeStochast name={self.name} distribution={self.distribution.value}>"

    def __getattr__(self, item):
        if item in self._extra:
            return self._extra[item]
        raise AttributeError(item)

    def to_plain(self):
        return {"name": self.name,
                "distribution": self.distribution.value,
                **self._extra}

    @classmethod
    def from_plain(cls, data):
        if not data:
            return cls()
        return cls(**data)