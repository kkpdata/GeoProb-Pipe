import plotly.graph_objects as go
from geoprob_pipe.comparisons.result_collect import ComparisonCollecter


def dumbbell_uittredepunt(comparison: ComparisonCollecter,
                          export: bool = False):
    df_result1 = (comparison.df1_beta_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta1"}))
    df_result2 = (comparison.df2_beta_uittredepunten[
        ["uittredepunt_id", "beta"]].rename(columns={"beta": "beta2"}))

    df = df_result1.merge(df_result2, on="uittredepunt_id")

    fig = go.Figure()

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
    fig.update_layout(
        title="Dumbbell Plot: Uittredepunt Beta Comparison",
        xaxis_title="Uittredepunt ID",
        yaxis_title="β-value"
    )
    fig.show()
    return
