class WaterlevelStatistics:
    """WaterlevelStatistics class which stores data related to the waterlevels statistics (Gumbel fit)"""

    def __init__(self, MU: float, SIGMA: float) -> None:
        """Initialize WaterlevelStatistics class which stores data related to the waterlevels statistics (Gumbel fit)

        Args:
            MU (float): mode (modus) of the load (water level) uncertainty distribution
            SIGMA (float): standard deviation of the load (water level) uncertainty distribution
        """
        self.mu = MU
        self.sigma = SIGMA
