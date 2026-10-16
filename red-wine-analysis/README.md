# 🍷 레드 와인 품질 데이터 분석

UCI/Kaggle의 **Red Wine Quality**(Cortez et al., 2009) 데이터로 와인 품질을 통계 분석하는 프로젝트입니다.

## 파일 구성

```
red-wine-analysis/
├── notebook.ipynb   # 주피터 노트북 (분석 전체 과정 + 실행 결과 포함)
├── dashboard.py     # Streamlit 웹 대시보드 보고서
├── data/
│   └── winequality-red.csv
└── requirements.txt
```

## 실행 방법

### 1) 패키지 설치
```
python -m pip install -r requirements.txt
```

### 2) 주피터 노트북
```
jupyter notebook notebook.ipynb      # 브라우저에서 열기
```
(노트북은 이미 실행 결과가 저장되어 있어 바로 읽어볼 수 있습니다)

### 3) 웹 대시보드 (Streamlit)
```
streamlit run dashboard.py
```
실행하면 브라우저(`http://localhost:8501`)에서 대시보드가 열립니다.

메뉴 구성: 개요 · 데이터 탐색 · 상관관계 · 그룹 비교 & t-검정 · 품질 예측 · 결론

## 데이터 출처
- UCI Machine Learning Repository — Wine Quality: <https://archive.ics.uci.edu/dataset/186/wine+quality>
- Cortez et al. (2009). *Modeling wine preferences by data mining from physicochemical properties*.
