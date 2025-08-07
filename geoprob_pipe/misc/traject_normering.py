import scipy.stats as sct


class TrajectNormering:

    def __init__(
            self,
            traject_naam: str = 'Elden-Heteren',  # Wat dummy waarden voor uitproberen class
            signaleringswaarde: int = 30_000,  # In jaren
            ondergrens: int = 10_000,  # In jaren
            w: float = 0.24,  # TODO Nu Must Klein: naam toevoegen van afkorting
            traject_lengte: float = 25362.572019,  # lengte van dijktraject
            norm_is_ondergrens: bool = True,
            bovenrivierengebied: bool = True,
    ):
        self.traject_naam: str = traject_naam
        self.signaleringswaarde: int = signaleringswaarde
        self.ondergrens: int = ondergrens
        self.w: float = w
        self.traject_lengte: float = traject_lengte
        self.bovenrivierengebied: bool = bovenrivierengebied

        # Parameters
        self.faalkanseis_signaleringswaarde = 1.0 / self.signaleringswaarde
        self.faalkanseis_ondergrens = 1.0 / self.ondergrens
        self.faalkanseis_norm = self.faalkanseis_ondergrens
        if not norm_is_ondergrens:
            self.faalkanseis_norm = self.signaleringswaarde
        self.beta_norm = sct.norm.ppf(self.faalkanseis_norm)
        self.n_dsn = 1 + (0.9 * self.traject_lengte) / 300.0
        if not self.bovenrivierengebied:
            self.n_dsn = 1 + (0.4 * self.traject_lengte) / 300.0
        # TODO Nu Must Later: Eigenlijk hoofdletter N_dsn. Maar ipv afkorting naam gebruiken?
        self.faalkanseis_sign_dsn = (self.w * self.faalkanseis_signaleringswaarde) / self.n_dsn
        self.beta_sign_dsn = sct.norm.ppf(self.faalkanseis_sign_dsn)
        self.faalkanseis_ond_dsn = (self.w * self.faalkanseis_ondergrens) / self.n_dsn
        self.beta_ond_dsn = sct.norm.ppf(self.faalkanseis_ond_dsn)
        self.beta_categorie_grenzen = {
            "I": [
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn / 30),
                50
            ],
            "II": [
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn),
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn / 30),
            ],
            "III": [
                -1 * sct.norm.ppf(self.faalkanseis_ond_dsn),
                -1 * sct.norm.ppf(self.faalkanseis_sign_dsn),
            ],
            "IV": [
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens),
                -1 * sct.norm.ppf(self.faalkanseis_ond_dsn),
            ],
            "V": [
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens * 30),
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens),
            ],
            "VI": [
                -50,
                -1 * sct.norm.ppf(self.faalkanseis_ondergrens * 30),
            ],
        }
