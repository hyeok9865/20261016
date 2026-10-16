# 데이터 분석 입문 · 확률과 통계 슬라이드덱

reveal.js 기반 HTML 슬라이드덱 프로젝트입니다. 대상: **데이터 분석을 입문하는 대학 비전공자**.

## 실행 방법

브라우저에서 `index.html` 열기 → PPT형 / Discord형 중 선택.
(파일이 안 열리면 `python -m http.server` 등 로컬 서버 사용 권장)

## 폴더 구조

```
1016/
├── index.html           # 랜딩 페이지 (디자인 2종 선택)
├── deck-ppt.html        # [Design 1] PPT형 덱 (대학 강의식)
├── deck-discord.html    # [Design 2] Discord형 덱 (DESIGN.md 토큰)
├── slides/              # (마크다운 소스 보관용)
├── assets/
│   ├── css/
│   │   ├── ppt.css      # PPT형 스타일 토큰
│   │   └── discord.css  # Discord 스타일 토큰
│   ├── js/              # reveal.js 설정
│   └── images/
├── references/          # 출처 자료 (papers/ · links.md)
└── _inbox/              # 사용자가 투입한 참고자료
    ├── DESIGN.md        # Discord 디자인 시스템 (디자인 토큰 원본)
    └── liberary.md      # (입력 대기)
```

## 디자인 컨셉

- **PPT형** (`deck-ppt.html`, `assets/css/ppt.css`): 흰 배경 + 남색(#1f3864)/파랑(#2e75b6) 헤딩, 정의 박스·예시 박스·표·수식 박스. 대학 강의용 무난한 레이아웃.
- **Discord형** (`deck-discord.html`, `assets/css/discord.css`): `_inbox/DESIGN.md` 토큰 반영. 인디고 캔버스(#0a0d3a) + 블러플(#5865f2)·마젠타(#ec48bd)·그린(#35ed7e), Space Grotesk All-caps, 40px+ 라운드 카드.

## 하이라이트 샘플 슬라이드 (양쪽 동일 구성, 7장)

1. 커버 → 2. 차시 개요 → 3. 핵심 개념(데이터와 변수) → 4. 확률의 기초 → 5. 평균·표준편차 수식 → 6. 정규분포 → 7. 다음 차시

## 소통 규칙

1. 새 슬라이드/토픽 추가 → 해당 덱의 `<section>` 추가 (HTML 직접 작성 방식)
2. 출처 표기 → 슬라이드 하단 `<div class="ref">`, 링크는 `references/links.md`에 기록
3. 수식 → KaTeX (`$..$` / `$$..$$`)
4. 디자인 토큰 변경 → `assets/css/*.css` 수정
5. `_inbox/`에 참고자료를 넣어주시면 그 내용으로 슬라이드를 채웁니다
