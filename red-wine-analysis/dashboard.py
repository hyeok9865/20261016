# -*- coding: utf-8 -*-
"""Red Wine Quality 데이터 분석 대시보드"""
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

st.set_page_config(page_title="레드 와인 품질 분석", page_icon="🍷", layout="wide")

# ---------------- 한글 폰트 ----------------
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")

try:
    fm._load_fontmanager(try_read_cache=False)
except Exception:
    pass
fonts = {f.name for f in fm.fontManager.ttflist}
korean_font = next((f for f in ["Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans KR"] if f in fonts), None)
if korean_font:
    plt.rcParams["font.family"] = korean_font
plt.rcParams["axes.unicode_minus"] = False

TEMPLATE = "plotly_white"
COLORS = px.colors.qualitative.Set2


@st.cache_data
def load_data():
    df = pd.read_csv("data/winequality-red.csv")
    df["quality_group"] = pd.cut(df["quality"], bins=[0, 4, 6, 10], labels=["나쁨 (≤4)", "보통 (5~6)", "좋음 (≥7)"])
    return df


df = load_data()
key_cols = ["fixed acidity", "volatile acidity", "citric acid", "residual sugar", "chlorides",
            "density", "pH", "sulphates", "alcohol"]

st.sidebar.title("🍷 Red Wine Quality")
st.sidebar.markdown("**UCI / Kaggle** · Cortez et al. (2009) · 1,599행")
st.sidebar.markdown("---")
menu = st.sidebar.radio("메뉴", ["📌 개요", "📊 데이터 탐색", "📈 상관관계", "⚖️ 그룹 비교 & t-검정", "🤖 품질 예측", "📝 결론"])

# =========================================================
if menu == "📌 개요":
    st.title("레드 와인 품질 데이터 분석 대시보드")
    st.caption("와인의 물리·화학적 특성 11가지로 품질(3~8)을 통계적으로 분석한 리포트")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 와인 수", f"{len(df):,}개")
    c2.metric("변수 개수", f"{df.shape[1] - 2}개")
    c3.metric("평균 품질", f"{df['quality'].mean():.2f} / 10")
    c4.metric("좋은 와인 비율(≥7)", f"{(df['quality'] >= 7).mean() * 100:.1f}%")

    st.markdown("### 📖 변수 설명")
    desc = pd.DataFrame([
        ["fixed acidity", "고정 산도 (주석산 g/dm³)", "많으면 신맛 ↑"],
        ["volatile acidity", "휘발성 산도 (초산 g/dm³)", "많으면 식초 냄새 ↑ (품질 ↓)"],
        ["citric acid", "구연산 (g/dm³)", "신맛/상쾌함"],
        ["residual sugar", "잔류 당 (g/dm³)", "달콤함"],
        ["chlorides", "염화물 (g/dm³)", "염분"],
        ["free sulfur dioxide", "유리 이산화황 (mg/dm³)", "산화 방지"],
        ["total sulfur dioxide", "총 이산화황 (mg/dm³)", "산화 방지 총량"],
        ["density", "밀도 (g/cm³)", "당/알코올과 관련"],
        ["pH", "pH", "산성도 (낮을수록 산성)"],
        ["sulphates", "황산염 (g/dm³)", "보존성 ↑"],
        ["alcohol", "알코올 도수 (% vol)", "높을수록 품질 ↑"],
        ["quality", "품질 점수 (0~10)", "분류 목표 (3~8 분포)"],
    ], columns=["변수", "의미", "품질과의 관계"])
    st.dataframe(desc, use_container_width=True, hide_index=True)

    st.markdown("### 🏆 핵심 요약 (한눈에)")
    st.success("**alcohol**이 많을수록, **volatile acidity(휘발성 산도)**가 적을수록 와인 품질이 높다. "
               "이 외에도 **sulphates**, **citric acid**가 품질과 양의 상관을 보인다.")

    fig = px.bar(df["quality"].value_counts().sort_index(), labels={"value": "빈도", "index": "quality"},
                 title="품질 점수 분포", color=df["quality"].value_counts().sort_index().index,
                 color_discrete_sequence=COLORS)
    fig.update_layout(template=TEMPLATE, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
elif menu == "📊 데이터 탐색":
    st.title("데이터 탐색 (EDA)")

    c1, c2, c3 = st.columns(3)
    c1.metric("결측치", f"{int(df.isna().sum().sum())}개")
    c2.metric("중복 행", f"{int(df.duplicated().sum())}개")
    c3.metric("행 × 열", f"{df.shape[0]} × {df.shape[1]}")

    st.markdown("### 📄 데이터 미리보기")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📐 기초 통계량")
    st.dataframe(df.describe().T.round(3), use_container_width=True)

    st.markdown("### 📊 변수 분포")
    col = st.selectbox("변수를 선택하세요", df.columns[:-1])
    fig = px.histogram(df, x=col, marginal="box", color_discrete_sequence=["#9e2a2b"],
                       title=f"{col} 분포")
    fig.update_layout(template=TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
elif menu == "📈 상관관계":
    st.title("상관관계 분석")
    st.markdown("**quality와 각 변수의 상관계수** 및 유의성(p<0.05)을 확인합니다.")

    corr = df.corr()
    corr_q = corr["quality"].drop("quality").sort_values(ascending=False)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("#### quality와의 상관계수")
        tab = pd.DataFrame({"변수": corr_q.index, "상관계수 r": corr_q.values.round(4)})
        tab["유의성"] = [("유의함" if stats.pearsonr(df[c], df["quality"])[1] < 0.05 else "유의하지 않음")
                       for c in corr_q.index]
        st.dataframe(tab, use_container_width=True, hide_index=True)
    with c2:
        fig = px.bar(corr_q, orientation="h", color=corr_q.values,
                     color_continuous_scale="RdBu_r", range_color=[-0.5, 0.5],
                     labels={"index": "", "value": "상관계수 r"}, title="quality와의 상관계수 막대그래프")
        fig.update_layout(template=TEMPLATE, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 상관 행렬 히트맵")
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, title="변수 간 상관행렬")
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
elif menu == "⚖️ 그룹 비교 & t-검정":
    st.title("품질 그룹별 비교")
    st.markdown("와인을 **나쁨(≤4) / 보통(5~6) / 좋음(≥7)** 세 그룹으로 나눠 비교합니다.")

    order = ["나쁨 (≤4)", "보통 (5~6)", "좋음 (≥7)"]
    st.markdown("#### 그룹별 인원")
    cnt = df["quality_group"].value_counts().reindex(order)
    st.dataframe(cnt.to_frame("와인 수").assign(비율=lambda x: (x["와인 수"] / len(df) * 100).round(1).astype(str) + "%"),
                 use_container_width=True)

    st.markdown("#### 그룹별 평균 비교")
    st.dataframe(df.groupby("quality_group", observed=True)[key_cols].mean().round(3).T, use_container_width=True)

    st.markdown("#### 상자그림")
    col = st.selectbox("비교할 변수를 선택하세요", key_cols, key="box")
    fig = px.box(df, x="quality_group", y=col, color="quality_group", category_orders={"quality_group": order},
                 title=f"품질 그룹별 {col}", color_discrete_sequence=COLORS)
    fig.update_layout(template=TEMPLATE, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 좋음 vs 나쁨 독립표본 t-검정")
    good = df[df["quality_group"] == "좋음 (≥7)"]
    bad = df[df["quality_group"] == "나쁨 (≤4)"]
    rows = []
    for c in key_cols:
        t, p = stats.ttest_ind(good[c], bad[c])
        rows.append({"변수": c, "t-통계량": round(t, 3), "p-value": round(p, 6),
                     "좋음 평균": round(good[c].mean(), 3), "나쁨 평균": round(bad[c].mean(), 3)})
    t_df = pd.DataFrame(rows).sort_values("p-value")
    t_df["결론"] = t_df["p-value"].apply(lambda p: "✅ 유의한 차이" if p < 0.05 else "❌ 차이 없음")
    st.dataframe(t_df, use_container_width=True, hide_index=True)
    st.caption("귀무가설(H₀): 두 그룹의 평균이 같다. p-value < 0.05이면 귀무가설을 기각한다.")

# =========================================================
elif menu == "🤖 품질 예측":
    st.title("RandomForest 품질 예측 (좋은 와인 여부)")
    st.markdown("**quality ≥ 7 = 좋은 와인(1)** 으로 변환해 분류하고, 어떤 변수가 중요한지 확인합니다.")

    @st.cache_data
    def run_model():
        mdf = df.copy()
        mdf["target"] = (mdf["quality"] >= 7).astype(int)
        X = mdf.drop(columns=["quality", "quality_group", "target"])
        y = mdf["target"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        rf = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
        rf.fit(X_tr, y_tr)
        acc = rf.score(X_te, y_te)
        imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
        return acc, imp, X_te, y_te, rf

    acc, imp, X_te, y_te, rf = run_model()

    c1, c2, c3 = st.columns(3)
    c1.metric("정확도 (Accuracy)", f"{acc * 100:.1f}%")
    c2.metric("좋은 와인 비율", f"{y_te.mean() * 100:.1f}%")
    c3.metric("모델", "Random Forest (300 trees)")

    st.markdown("#### 분류 리포트")
    report = classification_report(y_te, rf.predict(X_te), target_names=["보통 이하", "좋은 와인"], output_dict=True)
    rec = pd.DataFrame(report).T.reset_index().rename(columns={"index": "지표"})
    st.dataframe(rec[["지표", "precision", "recall", "f1-score", "support"]].round(3), use_container_width=True, hide_index=True)

    st.markdown("#### 변수 중요도")
    fig = px.bar(imp, orientation="h", color=imp.values, color_continuous_scale="Reds",
                 labels={"index": "", "value": "중요도"}, title="Feature Importance")
    fig.update_layout(template=TEMPLATE, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 혼동 행렬")
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_te, rf.predict(X_te))
    fig = px.imshow(cm, text_auto=True, x=["보통 이하", "좋은 와인"], y=["보통 이하", "좋은 와인"],
                    color_continuous_scale="Blues", title="Confusion Matrix")
    fig.update_layout(template=TEMPLATE)
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
elif menu == "📝 결론":
    st.title("결론 및 시사점")

    st.markdown("""
### 1) 데이터 특성
- 총 **1,599개** 레드 와인, 품질은 3~8 사이 분포. **5~6점이 대부분** (약 80%)이고 좋은 와인(≥7)은 **약 13.6%**뿐인 불균형 데이터입니다.

### 2) 품질을 결정하는 핵심 변수
| 순위 | 변수 | 상관계수 | 해석 |
|---|---|---|---|
| 1 | alcohol | +0.48 | 알코올 도수가 높을수록 품질 ↑ |
| 2 | volatile acidity | −0.39 | 휘발성 산도(식초 향) 많으면 품질 ↓ |
| 3 | sulphates | +0.25 | 황산염(보존성) ↑ → 품질 ↑ |
| 4 | citric acid | +0.23 | 구연산(상쾌한 산미) ↑ → 품질 ↑ |

### 3) 통계 검정
- 좋음(≥7) vs 나쁨(≤4) 그룹 간 대부분의 화학 성분 평균이 **통계적으로 유의하게 다릅니다** (t-검정, p<0.05).
- 특히 alcohol·volatile acidity의 차이가 두드러집니다.

### 4) 예측 모델
- RandomForest로 좋은 와인 여부를 분류했을 때 **변수 중요도 역시 alcohol·volatile acidity·sulphates가 최상위**로 나타나, 상관분석 결과와 일치합니다.
- 다만 화학 성분만으로는 좋은 와인을 완벽히 구분하기 어렵습니다(정확도 한계). 품질은 주관적 평가(테이스터)와 숙성·양조 공정 등 데이터에 없는 요소에도 영향을 받기 때문입니다.

### 5) 시사점
- **양조 관점**: 알코올 도수를 적정 수준으로 높이고, 휘발성 산도를 낮추는 관리가 품질 향상에 핵심입니다.
- **데이터 관점**: 비대칭(불균형) 분류 문제이므로, 더 좋은 모델을 위해 class weight나 SMOTE, 화이트 와인 데이터 병합 등을 고려할 수 있습니다.
    """)

    st.success("**분석 한 줄 요약:** 와인은 '알코올이 높고, 휘발성 산도가 낮을수록' 맛있다!")

# =========================================================
st.sidebar.markdown("---")
st.sidebar.caption(f"총 데이터 {len(df):,}행 · 결측치 {int(df.isna().sum().sum())}개 · 출처: UCI Wine Quality")
