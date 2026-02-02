from __future__ import annotations
import os
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import TYPE_CHECKING, Dict, List
if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


class IciclePlot:
    def __init__(self, geoprob_pipe: GeoProbPipe, export: bool = False):
        self.geoprob_pipe: GeoProbPipe = geoprob_pipe
        self.export: bool = export
        self.fig = go.Figure()
        self._setup_df()
        self._plot()
        self._update_layout()
        self._optionally_export()

    def _setup_df(self):
        # Per element parent_name, label, pof, beta
        df_traject = self.geoprob_pipe.results.df_beta_traject
        df_vakken = self.geoprob_pipe.results.df_beta_vakken
        # Remove vak without utp
        mask_vakken = df_vakken["pof"] != 0
        df_vakken = df_vakken[mask_vakken].copy()
        df_utp = self.geoprob_pipe.results.df_beta_uittredepunten
        df_scen = self.geoprob_pipe.results.df_beta_scenarios
        df_lim = self.geoprob_pipe.results.df_beta_limit_states

        # traject
        mask_traject = df_traject["method"] == "Sum of vakken"
        df_icicle: pd.DataFrame = df_traject.loc[
            mask_traject, ["upper_bound_pof", "lower_bound_beta"]
            ]
        df_icicle["parent_name"] = ""
        df_icicle["label"] = "Traject"
        df_icicle["id"] = "1"
        df_icicle = df_icicle.rename(columns={"upper_bound_pof": "pof",
                                              "lower_bound_beta": "beta"})
        # vakken
        df_vakken["label"] = "Vak_" + df_vakken["vak_id"].astype(str)
        mdf_vakken = df_vakken[["label", "pof", "beta"]].copy()
        mdf_vakken["parent_name"] = "1"
        mdf_vakken["id"] = "1_" + df_vakken["vak_id"].astype(str)
        df_icicle = pd.concat([df_icicle, mdf_vakken], ignore_index=True)

        # Uittredepunten
        df_utp["label"] = "UTP_" + df_utp["uittredepunt_id"].astype(str)
        df_utp["parent_name"] = "1_" + df_utp["vak_id"].astype(str)
        df_utp["id"] = (
            "1_" + df_utp["vak_id"].astype(str)
            + "_" + df_utp["uittredepunt_id"].astype(str)
            )
        df_utp = df_utp.rename(columns={"failure_probability": "pof"})
        mdf_utp = df_utp[
            ["parent_name", "label", "id", "beta", "pof"]
                         ].copy()
        df_icicle = pd.concat([df_icicle, mdf_utp], ignore_index=True)

        # Scenarios
        df_scen = df_scen.rename(
            columns={"failure_probability": "pof"}
            )
        df_scen["label"] = (
            df_scen["ondergrondscenario_id"].astype(str)
            + "_" + df_scen["uittredepunt_id"].astype(str)
            )
        df_scen["parent_name"] = (
            "1_" + df_scen["vak_id"].astype(str)
            + "_" + df_scen["uittredepunt_id"].astype(str)
            )
        df_scen["id"] = (
            "1_" + df_scen["vak_id"].astype(str)
            + "_" + df_scen["uittredepunt_id"].astype(str)
            + "_" + df_scen["ondergrondscenario_id"].astype(str)
            )
        mdf_scenarios = df_scen[
            ["parent_name", "label", "id", "beta", "pof"]
            ].copy()
        df_icicle = pd.concat([df_icicle, mdf_scenarios])

        # limit states
        df_lim["parent_name"] = (
            "1_" + df_lim["vak_id"].astype(str)
            + "_" + df_lim["uittredepunt_id"].astype(str)
            + "_" + df_lim["ondergrondscenario_id"].astype(str)
            )
        df_lim = df_lim.rename(
            columns={"limit_state": "label",
                     "failure_probability": "pof"}
            )
        df_lim["id"] = (
            "1_" + df_lim["vak_id"].astype(str)
            + "_" + df_lim["uittredepunt_id"].astype(str)
            + "_" + df_lim["ondergrondscenario_id"].astype(str)
            + "_" + df_lim["label"].astype(str).str[-1]
            )
        mdf_lim = df_lim[
            ["parent_name", "label", "id", "beta", "pof"]
        ].copy()
        df_icicle = pd.concat([df_icicle, mdf_lim])
        df_icicle["color"] = df_icicle.apply(
            lambda row: self._beta_to_color(row["beta"]), axis=1
            )
        self.df_icicle = df_icicle

    def _beta_to_color(self, beta: float) -> str:
        cg: Dict[str, List[float]] = self.geoprob_pipe.input_data.traject_normering.riskeer_categorie_grenzen
        # labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]
        colors = [
            "rgba(30,141,41,0.6)",  # +III
            "rgba(146,206,90,0.6)",  # +II
            "rgba(198,226,176,0.6)",  # +I
            "rgba(255,255,0,0.6)",  # 0
            "rgba(254,165,3,0.6)",  # -I
            "rgba(255,0,0,0.6)",  # -II
            "rgba(177,33,38,0.6)",  # -III
        ]
        for i, grens in enumerate(cg):
            beta_min, beta_max = cg[grens]

            if beta_min < np.log10(2):
                beta_min = np.log10(2)

            if beta_min <= beta < beta_max:
                return colors[i]
        return "rgba(128,128,128,0.6)"

    def _plot(self):
        df_icicle = self.df_icicle
        df_icicle["value"] = 1
        self.fig.add_trace(go.Icicle(
            ids=df_icicle["id"],
            labels=df_icicle["label"],
            parents=df_icicle["parent_name"],
            values=df_icicle["value"],
            marker=dict(colors=df_icicle["color"]),
            customdata=np.stack([df_icicle["pof"], df_icicle["beta"]], axis=1),
            texttemplate=(
                "%{label}<br>"
                "Pof: %{customdata[0]:.3e}<br>"
                "Beta: %{customdata[1]:.2f}"
            ),
            maxdepth=3,
        ))

    def _update_layout(self):
        self.fig.update_layout(
            title="Icicleplot van assemblage faalkansen",
            width=1400,
            height=900,
            margin=dict(t=50, l=25, r=25, b=25)
            )

    def _optionally_export(self):
        if self.export:
            path = self.geoprob_pipe.visualizations.graphs.export_dir
            self.fig.write_html(
                os.path.join(path, 'Icicle_assemblage.html'),
                include_plotlyjs='cdn'
                )
