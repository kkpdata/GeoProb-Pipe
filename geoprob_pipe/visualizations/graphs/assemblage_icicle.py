from __future__ import annotations
import os
import plotly.graph_objects as go
import pandas as pd
from typing import TYPE_CHECKING, Dict, List, cast

from pandas import Series, DataFrame

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
        # Per element parent_name, label, pf, beta
        df_traject = self.geoprob_pipe.results.df_beta_traject
        df_vakken = self.geoprob_pipe.results.df_beta_WBI_vakken
        df_vakken = df_vakken.rename(columns={"beta_dsn": "beta",
                                              "pf_dsn(max)": "pf"})

        # Remove vak without utp
        mask_vakken = df_vakken["pf"] != 0
        df_vakken = df_vakken[mask_vakken].copy()

        df_utp = self.geoprob_pipe.results.df_beta_uittredepunten
        df_scen = self.geoprob_pipe.results.df_beta_scenarios_final
        df_lim = self.geoprob_pipe.results.df_beta_limit_states

        # traject
        mask_traject = df_traject["method"] == "Sum of vakken"
        df_icicle: pd.DataFrame = df_traject.loc[
            mask_traject, ["upper_bound_pof", "lower_bound_beta"]
            ]
        df_icicle["parent_name"] = ""
        df_icicle["label"] = "Traject"
        df_icicle["id"] = "1"
        df_icicle["value"] = 1.0
        df_icicle = df_icicle.rename(columns={"upper_bound_pof": "pf",
                                              "lower_bound_beta": "beta"})
        # vakken
        df_vakken["label"] = "Vak: " + df_vakken["vak_id"].astype(str)
        df_vakken["parent_name"] = "1"
        self.n_vakken: int = len(df_vakken)
        df_vakken["id"] = "1_" + df_vakken["vak_id"].astype(str)

        # Add value for scaling leaves.
        df_vakken["value"] = 1.0 / self.n_vakken
        self.mdf_vakken = df_vakken[
            ["parent_name", "label", "id", "value", "beta", "pf"]
            ].copy()

        df_icicle = pd.concat([df_icicle, self.mdf_vakken], ignore_index=True)

        # Uittredepunten
        df_utp["label"] = "Uittredepunt: " + df_utp["uittredepunt_id"].astype(str)
        df_utp["parent_name"] = "1_" + df_utp["vak_id"].astype(str)
        df_utp["id"] = (
            "1_" + df_utp["vak_id"].astype(str)
            + "_" + df_utp["uittredepunt_id"].astype(str)
            )
        df_utp: DataFrame = df_utp.rename(columns={"failure_probability": "pf"})

        # Add value for scaling leaves.
        for pn in df_utp["parent_name"].unique():
            mask_utp: Series = cast(Series, df_utp["parent_name"] == str(pn))
            n_utp: int = mask_utp.sum()
            mask_icicle = df_icicle["id"] == str(pn)
            df_utp.loc[mask_utp, "value"] = (
                df_icicle.loc[mask_icicle, "value"].iloc[0] / n_utp
                )

        self.mdf_utp = df_utp[
            ["parent_name", "label", "id", "value", "beta", "pf"]
                         ].copy()

        df_icicle = pd.concat([df_icicle, self.mdf_utp], ignore_index=True)

        # Scenarios
        df_scen = df_scen.rename(
            columns={"failure_probability": "pf"}
            )
        df_scen["label"] = ("Ondergrondscenario: " +
                            df_scen["ondergrondscenario_id"].astype(str))
        df_scen["parent_name"] = (
            "1_" + df_scen["vak_id"].astype(str)
            + "_" + df_scen["uittredepunt_id"].astype(str)
            )
        df_scen["id"] = (
            "1_" + df_scen["vak_id"].astype(str)
            + "_" + df_scen["uittredepunt_id"].astype(str)
            + "_" + df_scen["ondergrondscenario_id"].astype(str)
            )
        # Add value for scaling leaves.
        for pn in df_scen["parent_name"].unique():
            mask_scen = cast(Series, df_scen["parent_name"] == str(pn))
            n_scen: int = mask_scen.sum()
            mask_icicle = df_icicle["id"] == str(pn)
            df_scen.loc[mask_scen, "value"] = (
                df_icicle.loc[mask_icicle, "value"].iloc[0] / n_scen
                )

        self.mdf_scenarios = df_scen[
            ["parent_name", "label", "id", "value", "beta", "pf"]
            ].copy()

        df_icicle = pd.concat([df_icicle, self.mdf_scenarios])

        # limit states
        df_lim["parent_name"] = (
            "1_" + df_lim["vak_id"].astype(str)
            + "_" + df_lim["uittredepunt_id"].astype(str)
            + "_" + df_lim["ondergrondscenario_id"].astype(str)
            )
        df_lim = df_lim.rename(
            columns={"limit_state": "label",
                     "failure_probability": "pf"}
            )
        df_lim["id"] = (
            "1_" + df_lim["vak_id"].astype(str)
            + "_" + df_lim["uittredepunt_id"].astype(str)
            + "_" + df_lim["ondergrondscenario_id"].astype(str)
            + "_" + df_lim["label"].astype(str).str[-1]
            )
        # Add value for scaling leaves.
        for pn in df_lim["parent_name"].unique():
            mask_lim = df_lim["parent_name"] == str(pn)
            mask_icicle = df_icicle["id"] == str(pn)
            df_lim.loc[mask_lim, "value"] = (
                df_icicle.loc[mask_icicle, "value"].iloc[0] / 3.0
                )

        self.mdf_lim = df_lim[
            ["parent_name", "label", "id", "value", "beta", "pf"]
        ].copy()
        df_icicle = pd.concat([df_icicle, self.mdf_lim])
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
        # Limit beta to range for colors
        if beta < 2:
            return "rgba(30,141,41,0.6)"
        elif beta > 20:
            return "rgba(177,33,38,0.6)"
        else:
            for i, grens in enumerate(cg):
                beta_min, beta_max = cg[grens]

                if beta_min <= beta < beta_max:
                    return colors[i]
        return "rgba(128,128,128,0.6)"

    def _plot(self):
        df = self.df_icicle

        mask_vakken = df["parent_name"].eq("1")
        df_vakken = df.loc[mask_vakken].sort_values(
            by="beta", ascending=True
        )
        mask_utp = df["parent_name"].str.count("_") == 1
        df_utp = df.loc[mask_utp].sort_values(
            by="beta", ascending=True
        )
        mask_scen = df["parent_name"].str.count("_") == 2
        df_scen = df.loc[mask_scen].sort_values(
            by="beta", ascending=True
        )
        mask_combined = mask_vakken | mask_utp | mask_scen
        df_rest = df.loc[~mask_combined]
        df_traject = df_rest.loc[df_rest["id"].eq("1")]
        df_rest = df_rest.loc[~df_rest["id"].eq("1")]

        df = pd.concat([df_traject, df_vakken, df_utp, df_scen, df_rest],
                       ignore_index=True)

        self.fig.add_trace(go.Icicle(
            ids=df["id"],
            labels=df["label"],
            parents=df["parent_name"],
            values=df["value"],
            sort=False,
            marker=dict(colors=df["color"]),
            customdata=df[["pf", "beta"]].to_numpy(),
            texttemplate=(
                "%{label}<br>"
                "Pof: %{customdata[0]:.3e}<br>"
                "Beta: %{customdata[1]:.2f}"
            ),
            maxdepth=2,
            branchvalues="remainder"
        ))

    def _update_layout(self):
        self.fig.update_layout(
            title="Icicle plot van assemblage faalkansen",
            height=self.n_vakken*50,
            margin=dict(t=50, l=25, r=25, b=25)
            )

    def _optionally_export(self):
        if self.export:
            path = self.geoprob_pipe.visualizations.graphs.export_dir

            # HTML-template met scrollbar container
            html_template = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
#scroll-container {{
    width: 100%;
    height: 900px;
    overflow-y: scroll;
    border: 1px solid #ccc;
}}
</style>
</head>
<body>

<div id="scroll-container">
    {self.fig.to_html(include_plotlyjs='cdn', full_html=False)}
</div>

</body>
</html>
"""

            export_file = os.path.join(path, "icicle_assemblage.html")
            with open(export_file, "w", encoding="utf-8") as f:
                f.write(html_template)
