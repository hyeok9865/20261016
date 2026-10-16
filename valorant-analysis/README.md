# VCT 2021–2023 데이터 분석 프로젝트

발로란트 e스포츠 최상위 대회 **Valorant Champions Tour (VCT) 2021–2023** 경기 데이터를 분석한 프로젝트입니다.

- 데이터 출처: [Kaggle – Valorant Champion Tour 2021-2023 Data](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data)
- 데이터 다운로드: `kagglehub.dataset_download("ryanluong1/valorant-champion-tour-2021-2023-data")`

## 📁 폴더 구조

```
valorant-analysis/
├── data/                     # 로컬 복사된 2021~2023 CSV (vct_2021/22/23)
├── notebooks/
│   └── valorant_analysis.ipynb   # 전체 분석 노트북 (실행된 출력 포함)
├── dashboard/
│   └── app.py                # Streamlit 웹 대시보드
├── data_loader.py            # 공용 데이터 로딩/전처리 모듈
├── build_notebook.py         # 노트북 생성 스크립트
├── requirements.txt
└── README.md
```

## 🚀 실행 방법

### 1. Jupyter Notebook

```bash
jupyter notebook notebooks/valorant_analysis.ipynb
```

(또는 VS Code / JupyterLab에서 `notebooks/valorant_analysis.ipynb` 열기)

### 2. 웹 대시보드 (Streamlit)

```bash
streamlit run dashboard/app.py
```

브라우저가 열리면 좌측 사이드바에서 **연도 선택**과 **메뉴**를 바꿔가며 탐색할 수 있습니다.

### 3. (선택) 노트북 재생성/재실행

```bash
python build_notebook.py              # 노트북 생성
python -m jupyter nbconvert --to notebook --execute notebooks/valorant_analysis.ipynb
```

## 📊 분석 내용

| 메뉴 | 주요 내용 |
|------|-----------|
| 개요 | 데이터 규모, 연도별 매치/선수/팀/맵 현황 |
| 선수 성적 | Rating·ACS·ADR·K/D·HS% 상위 선수, 지표 분포 |
| 에이전트 메타 | 연도별·맵별 픽률, 메타 변화 트렌드 |
| 맵 분석 | 맵 플레이 횟수, 공격/수비 사이드 승률 |
| 경기 & 라운드 | 세트 스코어, 경기 시간, 오버타임, 라운드 승리 방식 |
| 경제(에코) & 클러치 | 에코 라운드 승률, 클러치/멀티킬 TOP |

## 💡 핵심 인사이트

- 2021년은 지역별 챌린저스(오픈 예선 포함) 체제로 경기가 많았고, 2023년 국제 리그 체제로 개편되어 경기 수 급감.
- 에이전트 메타는 2021 Jett·Sova·Viper 중심에서 2023 신규 에이전트 등장과 함께 변화.
- 대부분 맵에서 수비측 승률 > 공격측 승률 (수비 친화적 밸런스).
- 라운드는 대부분 전멸(Elimination)로 종료, 풀바이(`$$$`) 라운드 승률이 에코 라운드보다 높음.

## ⚠️ 참고

- `data/` 폴더가 없으면 `data_loader.py`가 `kagglehub`으로 자동 다운로드합니다.
- Python 3.10+ 권장 (테스트 환경: Python 3.14, pandas 3.0, streamlit 1.66)
