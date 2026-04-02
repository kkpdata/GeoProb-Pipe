from pandas import DataFrame
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
from geoprob_pipe.input_data.traject_normering import TrajectNormering
from typing import Optional


def _add_beta_per_uittredepunt_points(
        self, df_for_graph: DataFrame, mask,
        name: str, color: str, value: bool
        ):
    """ Visualization of beta of uittredepunten.

    :param self: GraphBetaValuesSingleInteractive-object
    :param df_for_graph: Data to plot
    :param mask: Boolean Series for which uittredepunten to plot in graph. Either converged of unconverged points.
    :param name: Marker name
    :param color: Marker color
    :param value: Requested option: converged or not converged
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, "metrering"],
            y=df_for_graph.loc[mask, "beta"],
            mode='markers', marker=dict(symbol='circle', size=7, color=color),
            name=name,
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten", showlegend=value))


def _add_beta_per_uittredepunt_indication_above_plotting_range(
        self, df_for_graph: DataFrame, mask, name: str, color: str, value: bool):
    """ Indication to user that there are Beta results plotted outside
    the plotting range. In this case above range.
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, 'metrering'],
            y=[BETA_MAX - 0.5] * mask.sum(),
            mode='markers',
            marker=dict(symbol='triangle-up', size=7, color=color),
            name=name + " above plotted range",
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten",
            showlegend=value
        )
    )


def _add_beta_per_uittredepunt_indication_below_plotting_range(
        self, df_for_graph: DataFrame, mask, name: str, color: str, value: bool):
    """ Indication to user that there are Beta results plotted outside
    the plotting range. In this case below range.
    """

    self.fig.add_trace(
        go.Scatter(
            x=df_for_graph.loc[mask, 'metrering'],
            y=[BETA_MIN + 0.1] * mask.sum(),
            mode='markers',
            marker=dict(symbol='triangle-down', size=7, color=color),
            name=name + " below plotted range",
            customdata=df_for_graph.loc[mask, ["uittredepunt_id", "beta", "metrering"]],
            hovertemplate=("ID: %{customdata[0]}<br>" +
                           "Beta: %{customdata[1]:.3f}<br>" +
                           "Metrering: %{customdata[2]}"),
            legendgroup="Beta uittredepunten",
            showlegend=value
        )
    )


BETA_MIN = 2
BETA_MAX = 10
CATEGORY_COLORS = ["rgba(30,141,41,0.6)", "rgba(146,206,90,0.6)",
                   "rgba(198,226,176,0.6)", "rgba(255,255,0,0.6)",
                   "rgba(254,165,3,0.6)", "rgba(255,0,0,0.6)",
                   "rgba(177,33,38,0.6)"]
CATEGORY_LABELS = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]


class GraphBetaValuesSingleInteractive:

    def __init__(
            self,
            traject_normering: TrajectNormering,
            df_beta_vak: Optional[DataFrame] = None,
            beta_traject: Optional[float] = None,
            export_dir: Optional[str] = None
    ):
        """

        :param df_beta_vak: Optional DataFrame with columns vak_id,
        :param beta_traject:
        :param traject_normering:
        :param export_dir:
        """

        # Input
        self.df_beta_vak: Optional[DataFrame] = df_beta_vak
        self.beta_traject: Optional[float] = beta_traject
        self.traject_normering: TrajectNormering = traject_normering
        self.export_dir: str = export_dir

        # Validate input
        _validate_input(self)

        # Parameters
        self.fig = go.Figure()
        self.m_start = 0
        self.m_end = traject_normering.traject_lengte

        # Placeholders
        self.annotation_vak = []
        self.vak_lines = []
        self.annotation_label = []

        # Logic
        self._add_backgrond()
        self._add_beta_traject()
        self._add_beta_per_vak()
        # self._add_beta_per_scenario()  # TODO: Try to find and show nicely
        self._update_layout()
        self._optionally_export()

    def _add_backgrond(self):

        cg = self.traject_normering.riskeer_categorie_grenzen
        x_line = np.linspace(self.m_start, self.m_end)

        # Add 'Vak ID'-label
        self.annotation_vak.append(dict(
            x=0.5, y=np.log10(2.1), text="Vak ID:", showarrow=False, xanchor="left", yanchor="bottom",
            font=dict(color="black")))

        # Add vertical lines and vak label
        if self.df_beta_vak is not None:
            for _, vak in self.df_beta_vak.iterrows():
                self.vak_lines.append(dict(
                    x0=vak["m_start"], x1=vak["m_start"], y0=0, y1=1, xref="x", yref="paper",
                    line=dict(color="black", width=1)))
                self.vak_lines.append(dict(
                    x0=vak["m_end"], x1=vak["m_end"], y0=0, y1=1, xref="x", yref="paper",
                    line=dict(color="black", width=1)))
                self.annotation_vak.append(dict(
                    x=(vak["m_start"] + vak["m_end"]) / 2, y=np.log10(2), text=vak["id"], showarrow=False,
                    xanchor="center", yanchor="bottom", font=dict(color="black")))

        # Add category colors
        for i, grens in enumerate(cg):
            if cg[grens][0] <= 0:
                cg[grens][0] = np.log10(2)
            # Onderste lijn (zichtbaar)
            self.fig.add_trace(go.Scatter(
                x=x_line, y=[cg[grens][0]] * len(x_line), name=grens, mode="lines", line=dict(color="black", width=0.5),
                hoverinfo="skip", showlegend=False))
            # Bovenste lijn (onzichtbaar, zorgt voor fill)
            self.fig.add_trace(go.Scatter(
                x=x_line, y=[cg[grens][1]] * len(x_line), name=grens, mode="lines", fill="tonexty",
                line=dict(width=0), # geen bovenrand zichtbaar
                fillcolor=CATEGORY_COLORS[i % CATEGORY_COLORS.__len__()],  # kleur uit lijst
                hoverinfo="skip", showlegend=False))
            # Labels bij de ondergrens
            self.annotation_label.append(dict(
                x=x_line.max(), y=(np.log10(cg[grens][0]) + np.log10(cg[grens][1])) / 2,
                text=CATEGORY_LABELS[i % CATEGORY_LABELS.__len__()],
                showarrow=False, xanchor="left", yanchor="middle", font=dict(color="black", size=10), align="right"))

    def _add_beta_per_vak(self):
        if self.df_beta_vak is None:
            return

        # Plotting vak lines
        first = True
        for _, row in self.df_beta_vak.iterrows():
            self.fig.add_trace(go.Scatter(
                x=[row["m_start"], row["m_end"]], y=[row["beta"], row["beta"]], mode="lines",
                line=dict(color="black", width=2.5), name="Beta vakken", legendgroup="Beta vakken", showlegend=first,
                customdata=[[row["id"], row["beta"]]] * 2,
                hovertemplate="ID: %{customdata[0]}<br>" +
                              "Beta: %{customdata[1]:.3f}"))
            first = False

        # Above range triangle
        mask_high = self.df_beta_vak["beta"] > BETA_MAX
        first = True
        for _, row in self.df_beta_vak.loc[mask_high].iterrows():
            hovertemplate = ("ID: %{customdata[0]}<br>" +
                             "Beta: %{customdata[1]:.3f}<br>")
            if row["beta"] == np.inf:
                hovertemplate = ("ID: %{customdata[0]}<br>" +
                                 "Beta: inf <br>")
            self.fig.add_trace(go.Scatter(
                x=[(row["m_start"] + row["m_end"]) / 2], y=[BETA_MAX-0.1], mode="markers",
                marker=dict(color="black", symbol="triangle-up", size=9), name="Beta vakken (above plotted range)",
                customdata=[[row["id"], row["beta"]]], hovertemplate=hovertemplate,
                legendgroup="Beta vakken", showlegend=first))
            first = False

        # Below range triangle
        mask_low = self.df_beta_vak["beta"] < BETA_MIN
        first = True
        for _, row in self.df_beta_vak.loc[mask_low].iterrows():
            self.fig.add_trace(go.Scatter(
                x=[(row["m_start"] + row["m_end"]) / 2], y=[BETA_MIN+0.1], mode="markers",
                marker=dict(color="black", symbol="triangle-down", size=9), name="Beta vakken (below plotted range)",
                customdata=[[row["id"], row["beta"]]], legendgroup="Beta vakken", showlegend=first,
                hovertemplate="ID: %{customdata[0]}<br>" +
                              "Beta: %{customdata[1]:.3f}<br>"))
            first = False

    def _add_beta_traject(self):
        self.fig.add_trace(go.Scatter(
            x=[self.m_start, self.m_end], y=[self.beta_traject, self.beta_traject], mode="lines",
            line=dict(color="black", width=2.5, dash="dash"), name="Beta traject", showlegend=True,
            customdata=[[self.beta_traject]] * 2, hovertemplate="Beta: %{customdata[0]:.3f}"))

    def _update_layout(self):
        annotation = self.annotation_vak + self.annotation_label
        self.fig.update_layout(
            title="Betrouwbaarheidsindex",
            xaxis=dict(title="Metrering", type='linear', range=[0, self.m_end], showgrid=True, gridwidth=0.5,
                       gridcolor="gray"),
            yaxis=dict(title="Betrouwbaarheidsindex β [-]", type='log', range=[np.log10(2), np.log10(10)],
                       showgrid=True, gridwidth=0.5, gridcolor="gray", tickmode="array",
                       tickvals=[2, 3, 4, 5, 6, 7, 8, 9, 10], ticktext=[2, 3, 4, 5, 6, 7, 8, 9, 10]),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            annotations=annotation, shapes=self.vak_lines)
        # Toggles for annotations
        self.fig.update_layout(
            updatemenus=[
                dict(type="buttons", direction="right",buttons=[
                    dict(label="Show annotations", method="relayout",
                         args=["annotations", self.annotation_vak + self.annotation_label]),
                    dict(label="Hide annotations", method="relayout",args=["annotations", self.annotation_label]),
                    dict(label="Show vlines", method="relayout", args=["shapes", self.vak_lines]),
                    dict(label="Hide vlines", method="relayout", args=["shapes", []])
                ],
                     x=0.5, y=1.15, xanchor="center")])

    def _optionally_export(self):
        os.makedirs(self.export_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        timestamp_str = f"{timestamp}_"
        self.fig.write_html(
            os.path.join(self.export_dir, f"{timestamp_str}betrouwbaarheidsindex.html"), include_plotlyjs='cdn')


def _validate_input(self: GraphBetaValuesSingleInteractive):
    if self.df_beta_vak is not None:
        vak_columns = self.df_beta_vak.columns
        assert "id" in vak_columns, f"Required column 'id' not found in df_beta_vak."
        assert "m_start" in vak_columns, f"Required column 'm_start' not found in df_beta_vak."
        assert "m_end" in vak_columns, f"Required column 'm_end' not found in df_beta_vak."
        assert "beta" in vak_columns, (f"Required column 'beta' not found in df_beta_vak.\n"
                                       f"If you only have pf, use scipy.stats.norm.ppf(x) to convert to beta.")
