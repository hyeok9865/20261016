# -*- coding: utf-8 -*-
"""VCT 2021-2023 데이터 분석 대시보드 (Streamlit)

실행:  streamlit run dashboard/app.py
"""
import os
import sys

import matplotlib
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import data_loader as dl

# 한글 폰트
for f in ["Malgun Gothic", "Gulim"]:
    try:
        fm.fontManager.addfont(fm.findfont(fm.FontProperties(family=f)))
    except Exception:
        pass
matplotlib.rcParams["font.family"] = "Malgun Gothic"

VCOL = "#FF4655"
DARK = "#0F1923"
GRAY = "#768079"

st.set_page_config(page_title="VCT 2021-2023 분석 대시보드", layout="wide")

# ---------------- 데이터 캐시 ----------------
@st.cache_data(show_spinner="데이터 로딩 중...")
def load_all_data():
    ps = dl.clean_players_stats(dl.load_all("players_stats"))
    sc = dl.load_all("scores")
    msc = dl.load_all("maps_scores")
    mp = dl.load_all("maps_played")
    ks = dl.load_all("kills_stats")
    ar = dl.clean_pick_rates(dl.load_all("agents_pick_rates"))
    mst = dl.clean_maps_stats(dl.load_all("maps_stats"))
    eco = dl.load_all("eco_stats")
    wlm = dl.load_all("win_loss_methods")

    ps["is_total"] = ~ps["Agents"].astype(str).str.contains(",", na=True)
    ps_tot = ps[ps["is_total"]].copy()
    ps_tot["ACS"] = ps_tot["Average Combat Score"]
    ps_tot["ADR"] = ps_tot["Average Damage Per Round"]
    ps_tot["KPR"] = ps_tot["Kills Per Round"]
    ps_tot["HS%"] = ps_tot["Headshot %"]

    def parse_duration(s):
        s = str(s)
        try:
            parts = s.split(":")
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return np.nan

    msc = msc.copy()
    msc["DurationMin"] = msc["Duration"].apply(parse_duration) / 60

    ks2 = ks.dropna(subset=["Player"]).copy()
    for c in ["2k", "3k", "4k", "5k", "1v1", "1v2", "1v3", "1v4", "1v5"]:
        ks2[c] = pd.to_numeric(ks2[c], errors="coerce")
    ks2["Clutches"] = ks2[["1v1", "1v2", "1v3", "1v4", "1v5"]].fillna(0).sum(axis=1)
    ks2["MultiKills"] = ks2[["2k", "3k", "4k", "5k"]].fillna(0).sum(axis=1)

    eco2 = eco.dropna(subset=["Initiated"]).copy()
    eco2["WinRate"] = eco2["Won"] / eco2["Initiated"] * 100

    return {
        "ps_tot": ps_tot,
        "sc": sc,
        "msc": msc,
        "mp": mp,
        "ks2": ks2,
        "ar": ar,
        "mst": mst,
        "eco2": eco2,
        "wlm": wlm,
    }


D = load_all_data()

# ---------------- 사이드바 ----------------
st.sidebar.title("🎮 VCT 2021-2023")
st.sidebar.markdown("**Valorant Champions Tour** 데이터 분석")
st.sidebar.caption("출처: Kaggle `ryanluong1/valorant-champion-tour-2021-2023-data`")
YEARS = st.sidebar.multiselect("연도 선택", [2021, 2022, 2023], default=[2021, 2022, 2023])

page = st.sidebar.radio(
    "메뉴",
    ["개요", "선수 성적", "에이전트 메타", "맵 분석", "경기 & 라운드", "경제(에코) & 클러치"],
)

st.sidebar.markdown("---")
st.sidebar.caption("데이터 로딩: kagglehub + 로컬 캐시")


def filt(df, col="year"):
    if col in df.columns:
        return df[df[col].isin(YEARS)]
    return df


# ---------------- 페이지: 개요 ----------------
if page == "개요":
    st.title("🎮 Valorant Champions Tour (VCT) 2021–2023 데이터 분석")
    st.markdown(
        """
        발로란트 e스포츠의 최상위 대회인 **VCT** 2021~2023 경기 데이터를 분석한 대시보드입니다.
        선수 성적 · 에이전트 메타 · 맵 밸런스 · 라운드 · 경제까지 다양한 각도로 살펴볼 수 있습니다.
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    ps = filt(D["ps_tot"])
    sc = filt(D["sc"])
    mp = filt(D["mp"])
    c1.metric("선수 수", f"{ps['Player'].nunique():,}")
    c2.metric("팀 수", f"{ps['Teams'].nunique():,}")
    c3.metric("경기(매치) 수", f"{sc['Match Name'].nunique():,}")
    c4.metric("맵 플레이 수", f"{mp['Map'].count():,}")

    st.subheader("📅 연도별 규모")
    yearly = pd.DataFrame(
        {
            "matches": sc.groupby("year")["Match Name"].nunique(),
            "maps": mp.groupby("year")["Map"].count(),
            "players": ps.groupby("year")["Player"].nunique(),
            "teams": ps.groupby("year")["Teams"].nunique(),
        }
    ).reset_index()
    fig = px.bar(
        yearly.melt(id_vars="year", var_name="지표", value_name="값"),
        x="year", y="값", color="지표", barmode="group",
        color_discrete_sequence=[VCOL, "#1f77b4", "#2ca02c", "#ff7f0e"],
        labels={"year": "연도"},
        title="연도별 매치 / 맵 / 선수 / 팀 규모",
    )
    st.plotly_chart(fig, width="stretch")

    st.info(
        "💡 2021년에는 지역별 챌린저스(오픈 예선 포함) 대회가 많았고, 2023년에는 국제 리그 체제로 개편되어 "
        "경기 수가 크게 줄었습니다. 행 개수 차이는 실력 하락이 아니라 **대회 구조 개편** 때문입니다."
    )

# ---------------- 페이지: 선수 성적 ----------------
elif page == "선수 성적":
    st.title("🧑‍🚀 선수 개인 성적 분석")
    ps = filt(D["ps_tot"])
    min_rounds = st.slider("최소 플레이 라운드 수", 50, 1000, 200, step=50)
    elig = ps[ps["Rounds Played"] >= min_rounds]

    metric = st.selectbox(
        "지표 선택",
        ["Rating", "ACS", "ADR", "K/D", "KPR", "HS%", "Clutch Success %"],
    )
    top_n = st.slider("TOP N", 5, 50, 15, step=5)

    sub = (
        elig.groupby(["Player", "Teams", "year"])
        .agg(rounds=("Rounds Played", "sum"), val=(metric, "mean"))
        .reset_index()
        .query("rounds >= @min_rounds")
    )
    top = sub.sort_values("val", ascending=False).head(top_n).reset_index(drop=True)
    top["Rank"] = top.index + 1

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"TOP {top_n} - {metric}")
        st.dataframe(top[["Rank", "Player", "Teams", "year", "rounds", "val"]].rename(
            columns={"val": metric, "rounds": "총 라운드"}), width="stretch", hide_index=True)
    with col_b:
        fig = px.bar(
            top.sort_values("val"),
            x="val", y="Player", orientation="h",
            color="year", color_continuous_scale=["#0F1923", "#FF4655"],
            labels={"val": metric, "Player": ""},
            title=f"{metric} TOP {top_n}",
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, width="stretch")

    st.subheader("📊 지표 분포")
    dist = elig[[metric]].dropna()
    fig = px.histogram(dist, x=metric, nbins=50, color_discrete_sequence=[VCOL],
                       title=f"{metric} 분포 (최소 {min_rounds} 라운드 이상 선수)")
    fig.add_vline(x=dist[metric].mean(), line_dash="dash", line_color=DARK,
                  annotation_text=f"평균 {dist[metric].mean():.2f}")
    st.plotly_chart(fig, width="stretch")

    st.subheader("📈 연도별 상위 선수")
    top3 = (
        elig.groupby(["year", "Player", "Teams"])
        .agg(rounds=("Rounds Played", "sum"), rating=("Rating", "mean"))
        .reset_index()
        .query("rounds >= @min_rounds")
        .sort_values(["year", "rating"], ascending=[True, False])
        .groupby("year")
        .head(3)
        .reset_index(drop=True)
    )
    st.dataframe(top3, width="stretch", hide_index=True)

# ---------------- 페이지: 에이전트 메타 ----------------
elif page == "에이전트 메타":
    st.title("🃏 에이전트 메타 분석")
    ar = D["ar"]
    ar_map = ar[ar["Map"] == "All Maps"].copy()
    ar_map = ar_map[ar_map["year"].isin(YEARS)]

    meta_year = ar_map.groupby(["year", "Agent"])["Pick Rate"].mean().reset_index()

    st.subheader("연도별 에이전트 평균 픽률 (Heatmap)")
    pivot = meta_year.pivot(index="Agent", columns="year", values="Pick Rate")
    pivot = pivot.reindex(columns=sorted(YEARS))
    pivot = pivot.fillna(0).sort_values(by=pivot.columns[-1], ascending=False)
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values, x=pivot.columns.astype(str), y=pivot.index,
        colorscale="YlOrRd", text=np.round(pivot.values, 1), texttemplate="%{text}",
        zmin=0, zmax=100,
    ))
    fig.update_layout(title="에이전트 × 연도 픽률 (%)", height=700)
    st.plotly_chart(fig, width="stretch")

    st.subheader("📈 픽률 추이")
    agents = st.multiselect("에이전트 선택", sorted(meta_year["Agent"].unique()),
                            default=["jett", "viper", "killjoy", "fade", "chamber"])
    if agents:
        trace = meta_year[meta_year["Agent"].isin(agents)]
        fig = px.line(trace, x="year", y="Pick Rate", color="Agent", markers=True,
                      labels={"Pick Rate": "픽률 (%)", "year": "연도"})
        fig.update_layout(title="에이전트 픽률 추이", yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")

    st.subheader("🗺️ 2023 맵별 픽률")
    ar23 = ar[ar["year"] == 2023]
    pivot_map = ar23.pivot_table(index="Agent", columns="Map", values="Pick Rate", aggfunc="mean")
    pivot_map = pivot_map[[c for c in pivot_map.columns if c != "All Maps"]].fillna(0)
    fig = go.Figure(data=go.Heatmap(
        z=pivot_map.values, x=pivot_map.columns, y=pivot_map.index,
        colorscale="YlOrRd", text=np.round(pivot_map.values, 0).astype(int).astype(str),
        texttemplate="%{text}", zmin=0, zmax=100,
    ))
    fig.update_layout(title="2023 맵별 에이전트 픽률 (%)", height=700)
    st.plotly_chart(fig, width="stretch")

# ---------------- 페이지: 맵 분석 ----------------
elif page == "맵 분석":
    st.title("🗺️ 맵 분석")
    mp = D["mp"]
    map_cnt = mp["Map"].value_counts().rename("Total")
    map_year = mp[mp["year"].isin(YEARS)].groupby(["year", "Map"]).size().unstack(fill_value=0)

    st.subheader("맵 플레이 횟수 (연도별)")
    fig = px.bar(
        map_year.reset_index().melt(id_vars="year", var_name="Map", value_name="count"),
        x="Map", y="count", color="year", barmode="group",
        color_discrete_sequence=[VCOL, "#1f77b4", "#2ca02c"],
        labels={"count": "플레이 수", "Map": "맵"},
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("⚖️ 사이드(공격/수비) 승률")
    mst = D["mst"]
    ms_map = mst[mst["Map"] != "All Maps"]
    if YEARS:
        ms_map = ms_map[ms_map["year"].isin(YEARS)]
    side = ms_map.groupby("Map")[["Attacker Side Win Percentage", "Defender Side Win Percentage"]].mean().sort_values("Attacker Side Win Percentage")
    side_melt = side.reset_index().melt(id_vars="Map", var_name="Side", value_name="승률(%)")
    fig = px.bar(side_melt, x="Map", y="승률(%)", color="Side", barmode="group",
                 color_discrete_map={"Attacker Side Win Percentage": "#1f77b4",
                                     "Defender Side Win Percentage": VCOL})
    fig.add_hline(y=50, line_dash="dash", line_color=GRAY)
    st.plotly_chart(fig, width="stretch")

    st.info("💡 대부분의 맵에서 **수비측 승률이 공격측보다 높습니다**. 발로란트는 스파이크를 지키는 쪽이 유리한 구조입니다.")

    st.subheader("🗓️ 연도별 맵 도입 변화")
    t = map_year.astype(int)
    t["총합"] = t.sum(axis=1)
    st.dataframe(t, width="stretch")

# ---------------- 페이지: 경기 & 라운드 ----------------
elif page == "경기 & 라운드":
    st.title("🏟️ 경기 & 라운드 분석")
    sc = filt(D["sc"], "year")
    msc = D["msc"]

    st.subheader("매치 세트 스코어 분포")
    mres = sc.dropna(subset=["Team A Score", "Team B Score"]).copy()
    mres["Scoreline"] = mres["Team A Score"].astype(int).astype(str) + ":" + mres["Team B Score"].astype(int).astype(str)
    score_dist = mres["Scoreline"].value_counts().head(12)
    fig = px.bar(score_dist, color_discrete_sequence=[VCOL], labels={"index": "세트 스코어", "value": "매치 수"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.subheader("⏱️ 맵 경기 지속시간")
    dur = msc.dropna(subset=["DurationMin"])
    dur = dur[(dur["DurationMin"] < 120) & (dur["year"].isin(YEARS))]
    fig = px.histogram(dur, x="DurationMin", nbins=60, color_discrete_sequence=[DARK],
                       labels={"DurationMin": "분"})
    fig.add_vline(x=dur["DurationMin"].mean(), line_dash="dash", line_color=VCOL,
                  annotation_text=f"평균 {dur['DurationMin'].mean():.1f}분")
    fig.update_layout(title="맵별 경기 지속시간 분포")
    st.plotly_chart(fig, width="stretch")

    st.subheader("🔁 오버타임")
    ot = msc[(msc["Team A Score"] >= 13) & (msc["Team B Score"] >= 13)]
    ot = ot[ot["year"].isin(YEARS)] if len(ot) else ot
    st.metric("오버타임 맵 수", f"{len(ot):,}", delta=f"{(len(ot)/max(len(msc),1))*100:.1f}% of maps")

    st.subheader("🥇 라운드 승리 방식")
    wlm = D["wlm"]
    wlm = wlm[wlm["year"].isin(YEARS)]
    win_methods = ["Elimination", "Detonated", "Defused", "Time Expiry (No Plant)"]
    wlm_win = wlm.groupby("year")[win_methods].sum()
    wlm_ratio = wlm_win.div(wlm_win.sum(axis=1), axis=0) * 100
    fig = px.bar(wlm_ratio.reset_index().melt(id_vars="year", var_name="방식", value_name="비율(%)"),
                 x="year", y="비율(%)", color="방식", barmode="group")
    st.plotly_chart(fig, width="stretch")
    st.info("💡 대부분의 라운드는 **전멸(Elimination)**로 끝납니다. 폭탄 폭발(Detonated)보다 해체(Defused) 승리가 많은 것은 수비 우위 구조를 반영합니다.")

# ---------------- 페이지: 경제 & 클러치 ----------------
else:
    st.title("💰 경제(에코) & 클러치 분석")

    st.subheader("라운드 유형별 승률")
    eco2 = D["eco2"]
    eco2 = eco2[eco2["year"].isin(YEARS)]
    eco_type = eco2.groupby("Type")["WinRate"].mean().sort_values().reset_index()
    fig = px.bar(eco_type, x="Type", y="WinRate", color_discrete_sequence=["#2ca02c"],
                 labels={"Type": "라운드 유형", "WinRate": "평균 승률(%)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.info("💡 `$`→`$$$`로 갈수록(풀바이) 승률이 높아집니다. 에코 라운드 승률이 낮아 **자원 관리**가 중요합니다.")

    st.subheader("연도별 유형별 승률")
    eco_year = eco2.groupby(["year", "Type"])["WinRate"].mean().unstack()
    st.dataframe(eco_year.round(2), width="stretch")

    st.divider()
    st.subheader("🃏 클러치 & 멀티킬 TOP 플레이어")
    ks2 = D["ks2"]
    tab1, tab2 = st.tabs(["클러치(1vN)", "멀티킬(2k/3k/4k/5k)"])
    with tab1:
        clutch_cols = ["1v1", "1v2", "1v3", "1v4", "1v5"]
        top_clutch = ks2.groupby("Player")[clutch_cols + ["Clutches"]].sum().sort_values("Clutches", ascending=False).head(20)
        st.dataframe(top_clutch, width="stretch")
        fig = px.bar(top_clutch.reset_index(), x="Player", y="Clutches",
                     color_discrete_sequence=[VCOL], labels={"Clutches": "클러치 수"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
    with tab2:
        mk_cols = ["2k", "3k", "4k", "5k"]
        top_mk = ks2.groupby("Player")[mk_cols + ["MultiKills"]].sum().sort_values("MultiKills", ascending=False).head(20)
        st.dataframe(top_mk, width="stretch")
        fig = px.bar(top_mk.reset_index(), x="Player", y="MultiKills",
                     color_discrete_sequence=["#1f77b4"], labels={"MultiKills": "멀티킬 수"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("📊 멀티킬 / 클러치 구성 비율")
    mk_total = ks2[["2k", "3k", "4k", "5k"]].fillna(0).sum()
    cl_total = ks2[["1v1", "1v2", "1v3", "1v4", "1v5"]].fillna(0).sum()
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(values=mk_total.values, names=mk_total.index, title="멀티킬 구성",
                     color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = px.pie(values=cl_total.values, names=cl_total.index, title="클러치(1vN) 구성",
                     color_discrete_sequence=px.colors.sequential.Reds)
        st.plotly_chart(fig, width="stretch")

    st.caption("모든 데이터는 Kaggle의 VCT 2021-2023 데이터셋을 기반으로 합니다.")
