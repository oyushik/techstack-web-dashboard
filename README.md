# 🚀 IT 채용정보 분석 대시보드

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

한국의 주요 IT 채용 플랫폼(Wanted, Jumpit, Rallit)에서 수집한 채용공고 데이터를 분석하고 시각화하는 인터랙티브 대시보드입니다. 실시간 기술 스택 트렌드 분석과 관련 학습 자료 추천 기능을 제공합니다.

![Dashboard Preview](data/wordcloud_TECH_STACK.png)

## 📋 프로젝트 개요

**개발 기간**: 2025.04.16 ~ 2025.04.22
**팀 구성**: 3명 (Backend 2명, Frontend 1명)

## 👥 팀 구성 및 역할

| 역할         | 이름   | 담당 업무                               | GitHub                                                |
| ------------ | ------ | --------------------------------------- | ----------------------------------------------------- |
| **Backend**  | 오유식 | 팀장, 프로젝트 기획, 데이터 수집 및 정제 | [oyushik](https://github.com/oyushik)                 |
| **Backend** | 김우준 | 데이터 시각화, 대시보드 연동 및 최적화 | [Ra1nJun](https://github.com/Ra1nJun)                 |
| **Frontend** | 김민정 | 웹 대시보드 구현, UI/UX 개선 | [Mineong](https://github.com/Mineong)       |

## ✨ 주요 기능

- 📊 **기술 스택 트렌드 분석**: TOP 20 기술 스택을 인터랙티브 그래프로 시각화
- 🔍 **직무별 분석**: 전체/백엔드/프론트엔드 직군별 데이터 필터링
- 🎯 **스킬 기반 검색**: 특정 기술 스택이나 키워드로 채용공고 검색
- 📺 **학습 자료 추천**: 선택한 기술의 YouTube 튜토리얼 자동 검색
- 💼 **실시간 채용정보**: Work24 API 연동으로 관련 채용공고 표시
- 📈 **데이터 시각화**: Plotly 기반의 동적 차트 및 워드클라우드

## 🏗️ 프로젝트 구조

```
project-data-scraping/
├── src/
│   ├── scrapers/              # 데이터 수집
│   │   ├── data_utils.py      # 공통 유틸리티
│   │   └── notebooks/         # 스크래핑 Jupyter 노트북
│   ├── processing/            # 데이터 전처리
│   │   └── csv_merge.py       # CSV 병합 및 중복 제거
│   ├── visualization/         # 데이터 시각화
│   │   └── notebooks/         # 시각화 노트북
│   └── dashboard/             # Streamlit 대시보드
│       ├── app.py             # 메인 애플리케이션
│       ├── charts.py          # 차트 생성
│       ├── data_loader.py     # 데이터 로딩
│       ├── renderer.py        # UI 렌더링
│       └── search/            # 외부 API 검색
│           ├── youtube.py
│           └── work24.py
├── data/                      # 데이터 파일
├── requirements.txt           # Python 의존성
└── README.md
```

## 🚦 시작하기

### 필수 요구사항

- Python 3.9 이상
- pip 패키지 관리자

### 설치

1. **저장소 클론**
   ```bash
   git clone https://github.com/your-username/project-data-scraping.git
   cd project-data-scraping
   ```

2. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **환경 변수 설정** (선택 사항)

   API를 사용하려면 `.env` 파일을 생성하고 API 키를 추가하세요:
   ```bash
   YOUR_YOUTUBE_API_KEY=your_api_key_here
   YOUR_WORK24_API_KEY=your_api_key_here
   ```

### 대시보드 실행

```bash
streamlit run src/dashboard/app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 대시보드를 확인할 수 있습니다.

### 외부 접속 허용 (옵션)

```bash
streamlit run src/dashboard/app.py --server.address=0.0.0.0 --server.port=8501
```

## 📊 데이터 수집 및 처리

### 1. 데이터 스크래핑

Jupyter 노트북을 사용하여 각 채용 플랫폼에서 데이터를 수집합니다:

- `src/scrapers/notebooks/scraping_wanted.ipynb` - Wanted
- `src/scrapers/notebooks/scraping_jumpit.ipynb` - Jumpit
- `src/scrapers/notebooks/scraping_rallit.ipynb` - Rallit

각 노트북에서 직군(`total`, `backend`, `frontend`)을 선택하여 실행합니다.

### 2. 데이터 병합

수집한 CSV 파일을 병합하고 중복을 제거합니다:

```bash
python src/processing/csv_merge.py
```

병합된 파일은 `data/merged_data_{category}.csv` 형식으로 저장됩니다.

### 3. 데이터 시각화

워드클라우드 및 기타 시각화를 생성합니다:

- `src/visualization/notebooks/visualization_wordcloud.ipynb`
- `src/visualization/notebooks/visualization_graph.ipynb`

## 🎯 주요 기능 사용법

### 기술 스택 분석

1. 대시보드에서 **"🧩 기술 스택 분석"** 탭 선택
2. 전체/백엔드/프론트엔드 버튼으로 직군 필터링
3. 그래프 막대를 클릭하여 해당 기술의 상세 정보 확인

### 스킬 검색

1. 사이드바에서 **"대표 스킬 선택"** 드롭다운 사용
2. 또는 **"키워드 검색"** 입력창에 직접 입력
3. 선택한 스킬의 YouTube 튜토리얼 및 채용공고 자동 표시

### 데이터 필터링

- **요약 정보**: 선택한 키워드 관련 공고 수 및 기업 수 표시
- **직무 분석**: 관련 직무 TOP 20 차트
- **데이터 테이블**: 페이지네이션 기능이 있는 상세 데이터 테이블

## 🔧 기술 스택

### 데이터 수집 & 처리
- **Python 3.9+**: 메인 언어
- **Pandas**: 데이터 처리 및 분석
- **Requests**: HTTP 요청

### 대시보드
- **Streamlit**: 웹 애플리케이션 프레임워크
- **Plotly**: 인터랙티브 차트 생성

### 외부 API
- **YouTube Data API v3**: 튜토리얼 검색
- **Work24 API**: 채용정보 조회

## 📝 데이터 구조

### CSV 파일 형식

수집된 데이터는 다음 컬럼을 포함합니다:

| 컬럼명 | 설명 |
|--------|------|
| `company` | 회사명 |
| `position` | 직무/포지션 |
| `skill` | 요구 기술 스택 (쉼표로 구분) |

### 스킬 데이터 정제

`data_utils.py`의 `filter_skill_data()` 함수가 다음 작업을 수행합니다:

- 한글 문자 제거
- 특수문자 정리 (# 및 + 제외)
- 중복 스킬 제거
- 정규화된 형식으로 변환

## 🤝 기여하기

기여는 언제나 환영합니다! 다음 단계를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔗 참고 자료

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📮 문의

프로젝트에 대한 질문이나 제안이 있으시면 Issue를 생성해주세요.

---
