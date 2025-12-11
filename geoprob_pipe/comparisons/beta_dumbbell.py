from __future__ import annotations
import os
import plotly.graph_objects as go
import pandas as pd
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from geoprob_pipe.comparisons import ComparisonCollecter


def _add_traces(comparison: ComparisonCollecter,
                df: pd.DataFrame,
                fig: go.Figure):

    hoverdata = df[["uittredepunt_id", "beta1", "beta2"]].to_numpy()
    symbol_map = {
        1: "circle",
        0: "x"
    }
    try:
        symbols = [symbol_map[b] for b in df["converged"]]
    except KeyError:
        df_conv = comparison.df1_beta_scenarios
        # TODO is dit correct? Mss inbouwen in
        # calculate_df_beta_per_uittredepunt
        df_conv = (df_conv.groupby("uittredepunt_id", as_index=False)
                   ["converged"].min())
        symbols = [symbol_map[b] for b in df_conv["converged"]]

    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["uittredepunt_id"], row["uittredepunt_id"]],
            y=[row["beta1"], row["beta2"]],
            mode="lines",
            showlegend=False,
            marker=dict(
                color="grey"
            )
        ))

    fig.add_trace(go.Scatter(
        x=df["uittredepunt_id"],
        y=df["beta1"],
        mode="markers",
        name=comparison.name_1 + ".geoprob_pipe.gpkg",
        marker=dict(
            symbol=symbols,
            color="green",
            size=10
            ),
        customdata=hoverdata,
        hovertemplate=(
            "Uittredepunt ID: %{customdata[0]}<br>"
            "β1: %{customdata[1]:.2f}<br>"
            "β2: %{customdata[2]:.2f}<br>"
            "<extra></extra>"
        )
    ))

    fig.add_trace(go.Scatter(
        x=df["uittredepunt_id"],
        y=df["beta2"],
        mode="markers",
        name=comparison.name_2 + ".geoprob_pipe.gpkg",
        marker=dict(
                color="blue",
                size=10
            ),
        customdata=hoverdata,
        hovertemplate=(
            "Uittredepunt ID: %{customdata[0]}<br>"
            "β2: %{customdata[2]:.2f}<br>"
            "β1: %{customdata[1]:.2f}<br>"
            "<extra></extra>"
        )
    ))
    # Empty trace for legend
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        marker=dict(
            symbol="x",
            color="white",
            size=10,
            line=dict(
                color="black",
                width=0.5
            )
        ),
        name="Not converged"
    ))
    return fig


def _add_vak_id(comparison: ComparisonCollecter,
                fig: go.Figure):
    vak_ids = comparison.df1_beta_uittredepunten["vak_id"].unique()
    for _, vak_id in enumerate(vak_ids):
        df_vak = comparison.df1_beta_uittredepunten
        uit_ids = df_vak.loc[df_vak["vak_id"] == vak_id, ["uittredepunt_id"]]

        min_id: int = uit_ids.min().iloc[0]
        max_id: int = uit_ids.max().iloc[0]

        fig.add_trace(go.Scatter(
            x=[min_id, max_id],
            y=[0, 0],
            mode="lines",
            line=dict(color="red",
                      width=2),
            showlegend=False,
            name=f"{vak_id}"
        ))

        fig.add_annotation(
            x=(min_id + max_id) / 2,
            y=-0.7,
            text=f"{vak_id}",
            showarrow=False,
            font=dict(size=10, color="black"),
            align="center"
        )
    return fig


def dumbbell_beta(comparison: ComparisonCollecter,
                  export: bool = False):
    df_result1 = (comparison.df1_beta_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta1"}))
    df_result2 = (comparison.df2_beta_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta2"}))

    df = df_result1.merge(df_result2, on="uittredepunt_id")

    fig = go.Figure()
    fig = _add_traces(comparison, df, fig)
    fig = _add_vak_id(comparison, fig)

    fig.update_layout(
        title="Uittredepunt Beta Comparison",
        xaxis_title="Uittredepunt ID",
        yaxis_title="β-value",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "dumbbell_beta.html"
            ), include_plotlyjs='cdn')
        fig.write_image(os.path.join(
            comparison.export_dir, "dumbbell_beta.png"
            ), format="png", scale=5,  width=1400)

    return fig


def dumbbell_uplift(comparison: ComparisonCollecter,
                    export: bool = False):

    df_result1 = (comparison.df1_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]
        ].rename(columns={"beta": "beta1",
                          "limit_state": "limit_state1"}))

    df_result1 = df_result1[df_result1["limit_state1"] == "calc_Z_u"]

    df_result2 = (comparison.df2_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]
        ].rename(columns={"beta": "beta2",
                          "limit_state": "limit_state2"}))

    df_result2 = df_result2[df_result2["limit_state2"] == "calc_Z_u"]

    df = df_result1.merge(df_result2, on="uittredepunt_id")

    fig = go.Figure()
    fig = _add_traces(comparison, df, fig)
    fig = _add_vak_id(comparison, fig)

    fig.update_layout(
        title="Uittredepunt Calc_Z_u Beta Comparison",
        xaxis_title="Uittredepunt ID",
        yaxis_title="β-value",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "dumbbell_uplift.html"
            ), include_plotlyjs='cdn')
        fig.write_image(os.path.join(
            comparison.export_dir, "dumbbell_uplift.png"
            ), format="png", scale=5,  width=1400)
    return fig


def dumbbell_heave(comparison: ComparisonCollecter,
                   export: bool = False):
    df_result1 = (comparison.df1_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]]
                  .rename(columns={"beta": "beta1",
                                   "limit_state": "limit_state1"}))
    df_result1 = df_result1[df_result1["limit_state1"] == "calc_Z_h"]
    df_result2 = (comparison.df2_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]]
                  .rename(columns={"beta": "beta2",
                                   "limit_state": "limit_state2"}))
    df_result2 = df_result2[df_result2["limit_state2"] == "calc_Z_h"]

    df = df_result1.merge(df_result2, on="uittredepunt_id")

    fig = go.Figure()
    fig = _add_traces(comparison, df, fig)
    fig = _add_vak_id(comparison, fig)

    fig.update_layout(
        title="Uittredepunt Calc_Z_h Beta Comparison",
        xaxis_title="Uittredepunt ID",
        yaxis_title="β-value",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "dumbbell_heave.html"
            ), include_plotlyjs='cdn')
        fig.write_image(os.path.join(
            comparison.export_dir, "dumbbell_heave.png"
            ), format="png", scale=5,  width=1400)
    return fig


def dumbbell_piping(comparison: ComparisonCollecter,
                    export: bool = False):
    df_result1 = (comparison.df1_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]]
                  .rename(columns={"beta": "beta1",
                                   "limit_state": "limit_state1"}))
    df_result1 = df_result1[df_result1["limit_state1"] == "calc_Z_p"]
    df_result2 = (comparison.df2_beta_limit_states[
        ["uittredepunt_id", "limit_state", "beta"]]
                  .rename(columns={"beta": "beta2",
                                   "limit_state": "limit_state2"}))
    df_result2 = df_result2[df_result2["limit_state2"] == "calc_Z_p"]

    df = df_result1.merge(df_result2, on="uittredepunt_id")

    fig = go.Figure()
    fig = _add_traces(comparison, df, fig)
    fig = _add_vak_id(comparison, fig)

    fig.update_layout(
        title="Uittredepunt Calc_Z_p Beta Comparison",
        xaxis_title="Uittredepunt ID",
        yaxis_title="β-value",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    if export:
        os.makedirs(comparison.export_dir, exist_ok=True)
        fig.write_html(os.path.join(
            comparison.export_dir, "dumbbell_piping.html"
            ), include_plotlyjs='cdn')
        fig.write_image(os.path.join(
            comparison.export_dir, "dumbbell_piping.png"
            ), format="png", scale=5,  width=1400)
    return fig
