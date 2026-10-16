# -*- coding: utf-8 -*-
"""발로란트 챔피언스 투어 (VCT) 2021-2023 데이터 로딩/전처리 모듈.

노트북과 대시보드가 공통으로 사용하는 데이터 로딩 유틸입니다.
데이터 소스: https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data
"""
from __future__ import annotations

import os

import kagglehub
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATA = os.path.join(BASE_DIR, "data")

YEARS = ["vct_2021", "vct_2022", "vct_2023"]
YEAR_LABELS = {y: int(y.split("_")[1]) for y in YEARS}

# (연도폴더, 상대경로) -> 캐시 키
FILES = {
    "players_stats": "players_stats/players_stats.csv",
    "scores": "matches/scores.csv",
    "maps_scores": "matches/maps_scores.csv",
    "maps_played": "matches/maps_played.csv",
    "kills_stats": "matches/kills_stats.csv",
    "team_mapping": "matches/team_mapping.csv",
    "agents_pick_rates": "agents/agents_pick_rates.csv",
    "maps_stats": "agents/maps_stats.csv",
    "eco_stats": "matches/eco_stats.csv",
    "win_loss_methods": "matches/win_loss_methods_count.csv",
    "overview": "matches/overview.csv",
}


def _local_path(year: str, key: str) -> str:
    return os.path.join(LOCAL_DATA, year, FILES[key])


def _download_base() -> str:
    """kagglehub 캐시 경로를 반환합니다. 없으면 다운로드합니다."""
    return kagglehub.dataset_download("ryanluong1/valorant-champion-tour-2021-2023-data")


def data_dir() -> str:
    """로컬 데이터 디렉토리 (우선 사용)"""
    if os.path.isdir(LOCAL_DATA) and os.listdir(LOCAL_DATA):
        return LOCAL_DATA
    return _download_base()


def load(year: str, key: str, **kwargs) -> pd.DataFrame:
    """연도별 CSV 하나를 로드합니다.

    year: 'vct_2021' | 'vct_2022' | 'vct_2023'
    key : FILES의 키 (예: 'players_stats')
    """
    p = _local_path(year, key)
    if not os.path.exists(p):
        p = os.path.join(_download_base(), year, FILES[key])
    return pd.read_csv(p, low_memory=False, **kwargs)


def load_all(key: str, **kwargs) -> pd.DataFrame:
    """세 연도 전체를 묶어 로드하고 year 컬럼을 추가합니다."""
    frames = []
    for y in YEARS:
        df = load(y, key, **kwargs)
        df["year"] = YEAR_LABELS[y]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


# ---------------- 전처리 헬퍼 ----------------

PCT_COLS = [
    "Kill, Assist, Trade, Survive %",
    "Headshot %",
    "Clutch Success %",
]


def _pct_to_float(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
        .replace({"nan": None, "None": None, "": None})
        .astype(float)
    )


def clean_players_stats(df: pd.DataFrame) -> pd.DataFrame:
    """players_stats 전처리: 퍼센트 스트링 -> 숫자, 클러치 파싱."""
    df = df.copy()
    for c in PCT_COLS:
        if c in df.columns:
            df[c] = _pct_to_float(df[c])
    # Clutches (won/played) -> "1/5" 형태 파싱
    if "Clutches (won/played)" in df.columns:
        clut = df["Clutches (won/played)"].astype(str)
        parts = clut.str.split("/", expand=True)
        df["Clutches Won"] = pd.to_numeric(parts[0], errors="coerce")
        df["Clutches Played"] = pd.to_numeric(parts[1], errors="coerce")
    # Kills:Deaths 스트링 -> 숫자
    if "Kills:Deaths" in df.columns:
        df["K/D"] = pd.to_numeric(df["Kills:Deaths"], errors="coerce")
    if "Rating" in df.columns:
        df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    return df


def clean_pick_rates(df: pd.DataFrame) -> pd.DataFrame:
    """agents_pick_rates 전처리: '91%' -> 91.0"""
    df = df.copy()
    df["Pick Rate"] = _pct_to_float(df["Pick Rate"])
    return df


def clean_maps_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Attacker Side Win Percentage"] = _pct_to_float(df["Attacker Side Win Percentage"])
    df["Defender Side Win Percentage"] = _pct_to_float(df["Defender Side Win Percentage"])
    df["Total Maps Played"] = pd.to_numeric(df["Total Maps Played"], errors="coerce")
    return df


def clean_win_loss(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = pd.to_numeric(df[c], errors="ignore")
    return df


# ---------------- 집계 헬퍼 ----------------

def top_players(df: pd.DataFrame, metric: str = "Rating", min_rounds: int = 100,
                min_matches: int = 1, top_n: int = 20) -> pd.DataFrame:
    """최소 라운드 이상 뛴 선수 중 지표 기준 상위 top_n."""
    df = clean_players_stats(df)
    g = (
        df.groupby(["Player", "Teams", "year"])
        .agg(
            n_maps=("Rounds Played", "count"),
            rounds=("Rounds Played", "sum"),
            **{
                metric: (metric, "mean"),
            },
        )
        .reset_index()
    )
    return g[g["rounds"] >= min_rounds].sort_values(metric, ascending=False).head(top_n)
