import plotly.graph_objects as go
import pandas as pd
from geoprob_pipe.comparisons.result_collect import ComparisonCollecter


def _add_traces(comparison: ComparisonCollecter,
                df: pd.DataFrame,
                fig: go.Figure):
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
        name=comparison.name_1,
        marker=dict(
                color="green",
                size=10
            )
    ))

    fig.add_trace(go.Scatter(
        x=df["uittredepunt_id"],
        y=df["beta2"],
        mode="markers",
        name=comparison.name_2,
        marker=dict(
                color="blue",
                size=10
            )
    ))
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

    fig.update_layout(
        title="Dumbbell Plot: Uittredepunt Beta Comparison",
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
    fig.show()
    return


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

    fig.update_layout(
        title="Dumbbell Plot: Uittredepunt Calc_Z_u Beta Comparison",
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
    fig.show()
    return


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

    fig.update_layout(
        title="Dumbbell Plot: Uittredepunt Calc_Z_h Beta Comparison",
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
    fig.show()
    return


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

    fig.update_layout(
        title="Dumbbell Plot: Uittredepunt Calc_Z_p Beta Comparison",
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
    fig.show()
    return
