from __future__ import annotations
import pandas as pd
from pandas import merge
import numpy as np
from scipy.stats import norm
import os
from datetime import datetime
import plotly.graph_objects as go
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geoprob_pipe import GeoProbPipe


def beta_to_color(beta: float, geoprob_pipe) -> str:
    """
    beta to RGBA color based on riskeer_categorie_grenzen
    """

    cg = geoprob_pipe.input_data.traject_normering.riskeer_categorie_grenzen

    labels = ["+III", "+II", "+I", "0", "-I", "-II", "-III"]
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

        # zelfde safeguard als in je bestaande code
        if beta_min <= 0:
            beta_min = np.log10(2)

        if beta_min <= beta < beta_max:
            return colors[i]

    return "rgba(200,200,200,0.6)"


def run_icicle(export: bool = True) -> go.Figure:
    """
    Horizontale Icicle (links → rechts)
    GeoProb data

    - Internal labels: leesbaar + uniek (pathbar + boom)
    - Display labels: naam + β
    - Kleuren op basis van β-categorie
    """

    labels = []
    parents = []
    values = []
    betas = []
    text = []
    colors = []

    def add(internal: str, parent: str, display: str, beta: float):
        labels.append(internal)
        parents.append(parent)
        values.append(1.0)
        betas.append(beta)
        text.append(display)
        colors.append(beta_to_color(beta, geoprob_pipe))

    LIMIT_STATE_MAP = {
        "calc_Z_u": "Uplift",
        "calc_Z_h": "Heave",
        "calc_Z_p": "Piping",
    }

    df_vak = geoprob_pipe.results.df_beta_vakken
    df_up = geoprob_pipe.results.df_beta_uittredepunten
    df_sc = geoprob_pipe.results.df_beta_scenarios
    df_ls = geoprob_pipe.results.df_beta_limit_states

    # ---- Traject ----
    df_vak["pf_vak"] = norm.cdf(-df_vak["beta"])
    pf_traj = float(
        df_vak["pf_vak"].sum()
    )  # traject kans bij benadering de som van vak kansen bespreken met Chris en Vincent
    beta_traj = -norm.ppf(pf_traj)
    traj_int = "Traject"
    traj_disp = f"Traject (β={beta_traj:.2f}, Pf={pf_traj:.2e})"
    add(traj_int, "", traj_disp, beta_traj)

    for _, vak in df_vak.iterrows():
        vak_id = int(vak["vak_id"])
        beta_vak = float(vak["beta"])

        vak_int = f"Vak {vak_id}"
        vak_disp = f"Vak {vak_id} (β={beta_vak:.2f})"
        add(vak_int, traj_int, vak_disp, beta_vak)

        df_up_vak = df_up[df_up["vak_id"] == vak_id]
        for _, up in df_up_vak.iterrows():
            up_id = int(up["uittredepunt_id"])
            beta_up = float(up["beta"])

            up_int = f"Uittredepunt {up_id} (Vak {vak_id})"
            up_disp = f"Uittredepunt {up_id} (β={beta_up:.2f})"
            add(up_int, vak_int, up_disp, beta_up)

            df_sc_up = df_sc[
                (df_sc["vak_id"] == vak_id) & (df_sc["uittredepunt_id"] == up_id)
            ]

            for _, sc in df_sc_up.iterrows():
                sc_id = sc["ondergrondscenario_id"]
                beta_sc = float(sc["beta"])

                sc_int = f"Scenario {sc_id} (Uittredepunt {up_id}, Vak {vak_id})"
                sc_disp = f"Scenario {sc_id} (β={beta_sc:.2f})"
                add(sc_int, up_int, sc_disp, beta_sc)

                df_ls_sc = df_ls[
                    (df_ls["vak_id"] == vak_id)
                    & (df_ls["uittredepunt_id"] == up_id)
                    & (df_ls["ondergrondscenario_id"] == sc_id)
                ]

                for _, ls in df_ls_sc.iterrows():
                    beta_ls = float(ls["beta"])
                    mech = LIMIT_STATE_MAP.get(ls["limit_state"], ls["limit_state"])

                    ls_int = f"{mech} (Scenario {sc_id}, UP {up_id})"
                    ls_disp = f"{mech} (β={beta_ls:.2f})"
                    add(ls_int, sc_int, ls_disp, beta_ls)

    fig = go.Figure(
        go.Icicle(
            labels=labels,
            parents=parents,
            values=values,
            text=text,
            textinfo="text",
            customdata=betas,
            marker=dict(colors=colors),
            branchvalues="remainder",
            tiling=dict(orientation="h"),
            pathbar=dict(visible=True),
            hovertemplate="<b>%{text}</b><br>β=%{customdata:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Overview betrouwbaarheidsindexen alle niveaus GeoProb-Pipe",
        margin=dict(t=50, l=20, r=20, b=20),
    )

    # Export
    if export:
        export_dir = geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(
            os.path.join(export_dir, f"icicle_overview_betas.html"),
            include_plotlyjs="cdn",
        )
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(
                os.path.join(export_dir, f"icicle_overview_betas.png"), format="png"
            )

    return fig


def run_icicle_scale(export: bool = True) -> go.Figure:
    """
    Horizontale Icicle (links → rechts)

    - Traject = 100%
    - Vak-breedte ∝ Pf_vak (met minimum + hernormalisatie)
    - Binnen elk vak: UP's relatief geschaald
    - Binnen elke UP: scenario's relatief geschaald
    - Binnen elk scenario: mechanismen relatief geschaald
    """

    import numpy as np
    from scipy.stats import norm

    labels = []
    parents = []
    values = []
    betas = []
    text = []
    colors = []

    # =====================
    # Helper: add node
    # =====================
    def add(internal, parent, display, beta, value):
        labels.append(internal)
        parents.append(parent)
        values.append(float(value))
        betas.append(float(beta))
        text.append(display)
        colors.append(beta_to_color(beta, geoprob_pipe))

    # =====================
    # Mechanisme namen
    # =====================
    LIMIT_STATE_MAP = {
        "calc_Z_u": "Uplift",
        "calc_Z_h": "Heave",
        "calc_Z_p": "Piping",
    }

    # =====================
    # Data
    # =====================
    df_vak = geoprob_pipe.results.df_beta_vakken.copy()
    df_up = geoprob_pipe.results.df_beta_uittredepunten
    df_sc = geoprob_pipe.results.df_beta_scenarios
    df_ls = geoprob_pipe.results.df_beta_limit_states

    df_vak["beta"] = df_vak["beta"].astype(float)

    # =====================
    # Traject Pf + vak-shares
    # =====================
    df_vak["pf_vak"] = norm.cdf(-df_vak["beta"])
    pf_traj = float(df_vak["pf_vak"].sum())
    beta_traj = -norm.ppf(pf_traj)

    # rauwe shares
    df_vak["vak_share_raw"] = df_vak["pf_vak"] / pf_traj if pf_traj > 0 else 0.0

    # adaptieve minimum-breedte
    TARGET_MIN_SHARE = 0.03
    N = len(df_vak)
    MIN_SHARE = min(TARGET_MIN_SHARE, 0.8 / N)

    df_vak["vak_share_floored"] = df_vak["vak_share_raw"].clip(lower=MIN_SHARE)
    df_vak["vak_share"] = (
        df_vak["vak_share_floored"] / df_vak["vak_share_floored"].sum()
    )

    # =====================
    # Traject (100%)
    # =====================
    traj_int = "Traject"
    traj_disp = f"Traject (β={beta_traj:.2f}, Pf={pf_traj:.2e})"
    add(traj_int, "", traj_disp, beta_traj, value=1.0)

    # =====================
    # Vak → UP → Scenario → Mechanisme
    # =====================
    for _, vak in df_vak.iterrows():
        vak_id = int(vak["vak_id"])
        beta_vak = float(vak["beta"])
        pf_vak = float(vak["pf_vak"])
        vak_share = float(vak["vak_share"])

        vak_int = f"Vak {vak_id}"
        vak_disp = f"Vak {vak_id} (β={beta_vak:.2f}, Pf={pf_vak:.2e})"
        add(vak_int, traj_int, vak_disp, beta_vak, value=vak_share)

        # ---------- Uittredepunten (relatief binnen vak) ----------
        df_up_vak = df_up[df_up["vak_id"] == vak_id].copy()
        n_up = len(df_up_vak)

        if n_up == 0:
            continue

        df_up_vak["up_share"] = vak_share / n_up

        for _, up in df_up_vak.iterrows():
            up_id = int(up["uittredepunt_id"])
            beta_up = float(up["beta"])
            up_share = float(up["up_share"])

            up_int = f"Uittredepunt {up_id} (Vak {vak_id})"
            up_disp = f"Uittredepunt {up_id} (β={beta_up:.2f})"
            add(up_int, vak_int, up_disp, beta_up, value=up_share)

            # ---------- Scenario's (relatief binnen UP) ----------
            df_sc_up = df_sc[
                (df_sc["vak_id"] == vak_id) & (df_sc["uittredepunt_id"] == up_id)
            ].copy()

            n_sc = len(df_sc_up)
            if n_sc == 0:
                continue

            df_sc_up["sc_share"] = up_share / n_sc

            for _, sc in df_sc_up.iterrows():
                sc_id = sc["ondergrondscenario_id"]
                beta_sc = float(sc["beta"])
                sc_share = float(sc["sc_share"])

                sc_int = f"Scenario {sc_id} (UP {up_id}, Vak {vak_id})"
                sc_disp = f"Scenario {sc_id} (β={beta_sc:.2f})"
                add(sc_int, up_int, sc_disp, beta_sc, value=sc_share)

                # ---------- Mechanismen (relatief binnen scenario) ----------
                df_ls_sc = df_ls[
                    (df_ls["vak_id"] == vak_id)
                    & (df_ls["uittredepunt_id"] == up_id)
                    & (df_ls["ondergrondscenario_id"] == sc_id)
                ].copy()

                n_ls = len(df_ls_sc)
                if n_ls == 0:
                    continue

                df_ls_sc["ls_share"] = sc_share / n_ls

                for _, ls in df_ls_sc.iterrows():
                    beta_ls = float(ls["beta"])
                    mech = LIMIT_STATE_MAP.get(ls["limit_state"], ls["limit_state"])
                    ls_share = float(ls["ls_share"])

                    ls_int = f"{mech} (Scenario {sc_id}, UP {up_id})"
                    ls_disp = f"{mech} (β={beta_ls:.2f})"
                    add(ls_int, sc_int, ls_disp, beta_ls, value=ls_share)

    # =====================
    # Icicle plot
    # =====================
    fig = go.Figure(
        go.Icicle(
            labels=labels,
            parents=parents,
            values=values,
            text=text,
            textinfo="text",
            customdata=betas,
            marker=dict(colors=colors),
            branchvalues="remainder",
            tiling=dict(orientation="h"),
            pathbar=dict(visible=True),
            hovertemplate="<b>%{text}</b><br>β=%{customdata:.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"Overview betrouwbaarheidsindexen alle niveaus GeoProb-Pipe",
        margin=dict(t=50, l=20, r=20, b=20),
    )
    # Export
    if export:
        export_dir = geoprob_pipe.visualizations.graphs.export_dir
        os.makedirs(export_dir, exist_ok=True)
        fig.write_html(
            os.path.join(export_dir, f"icicle_overview_betas.html"),
            include_plotlyjs="cdn",
        )
        if geoprob_pipe.software_requirements.chrome_is_installed:
            fig.write_image(
                os.path.join(export_dir, f"icicle_overview_betas.png"), format="png"
            )

    return fig
