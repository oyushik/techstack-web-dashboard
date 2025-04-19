import streamlit as st
import pandas as pd
# 필요한 모듈에서 함수 임포트
from web_load_data import load_all_data, count_skills
from web_charts import create_animated_bar_chart
from streamlit_plotly_events import plotly_events
import re # filter_data에서 사용
import web_search_youtube as yt # YouTube 검색 모듈
from dotenv import load_dotenv
import os
load_dotenv()
YOUR_YOUTUBE_API_KEY = os.getenv("YOUR_YOUTUBE_API_KEY")
from PIL import Image # 이미지 표시를 위한 PIL 모듈

# --- 클릭 이벤트 핸들러 함수 ---
def handle_chart_click(clicked_data, orientation="v"):
    """
    Plotly chart 클릭 이벤트 데이터를 처리하여 선택된 항목을 세션 상태에 추가하고 rerun을 요청합니다.

    Args:
        clicked_data: plotly_events 함수로부터 반환된 클릭 이벤트 데이터 목록 (list of dicts).
        orientation: 그래프의 방향 ('v' for vertical, 'h' for horizontal).
                    클릭된 항목의 이름을 가져올 때 사용됩니다.
    """
    if clicked_data:
        # 첫 번째 클릭된 데이터 포인트만 처리
        clicked_point = clicked_data[0]
        selected_item = None

        # 그래프 방향에 따라 클릭된 항목의 이름(값) 가져오기
        if orientation == "h":
            selected_item = clicked_point.get('y') # 가로 막대: Y축이 항목 이름
        else: # orientation == "v"
            selected_item = clicked_point.get('x') # 세로 막대: X축이 항목 이름

        # 유효한 항목 이름이 추출되었는지 확인
        if selected_item:
            # 클릭된 항목을 세션 상태 리스트에 추가 (중복 방지)
            # 'clicked_skills' 세션 상태는 setup_page에서 초기화되어야 합니다.
            if 'clicked_skills' not in st.session_state: # 방어적 코드 (setup_page에서 초기화 권장)
                st.session_state.clicked_skills = []

            if selected_item not in st.session_state.clicked_skills:
                st.session_state.clicked_skills.append(selected_item)
                # UI 갱신 및 plotly_events 상태 관리를 위해 render_id 증가 및 rerun 트리거
                if 'render_id' not in st.session_state: # 방어적 코드 (setup_page에서 초기화 권장)
                    st.session_state.render_id = 0
                st.session_state.render_id += 1
                # st.rerun() # 세션 상태 변경 사항을 반영하여 앱 다시 실행

# --- 클릭된 스킬 표시 함수 ---
def display_clicked_skills(current_chart_type):
    """
    클릭된 스킬 목록과 초기화 버튼을 표시합니다.
    세션 상태 st.session_state.clicked_skills의 값에 따라 표시 여부를 결정합니다.

    Args:
        current_chart_type: 현재 기술 스택 분석의 타입 ('total', 'backend', 'frontend') - 초기화 버튼 키에 사용.
    """
    # 세션 상태에 저장된 클릭된 스킬 목록을 확인
    clicked_skills_list = st.session_state.get('clicked_skills', [])

    # 목록이 비어있지 않으면 표시
    if clicked_skills_list:
        st.write("클릭된 기술 스택:", ", ".join(clicked_skills_list))

        # 선택 초기화 버튼
        # 버튼 키는 현재 차트 타입과 결합하여 고유하게 유지
        if st.button("클릭된 스킬 초기화", key=f"clear_clicked_{current_chart_type}"):
            # 버튼 클릭 시 세션 상태 초기화
            st.session_state.clicked_skills = []
            # plotly_events 상태 갱신을 위해 render_id 증가 (필요하다면)
            if 'render_id' in st.session_state:
                st.session_state.render_id += 1
            st.rerun()

# --- 페이지 설정 함수 ---
def setup_page():
    st.set_page_config(
        page_title="IT 채용정보 분석 대시보드",
        page_icon="📊",
        layout="wide" # 넓은 레이아웃 사용
    )

    # 세션 상태 초기화
    # 사이드바 멀티셀렉트용 스킬 목록
    if 'selected_skills' not in st.session_state:
        st.session_state.selected_skills = []
    # plotly_events 키 생성을 위한 고유 ID
    if 'render_id' not in st.session_state:
        st.session_state.render_id = 0
    # 기술 스택 분석 섹션에서 현재 선택된 차트 타입 (전체/백엔드/프론트엔드)
    if 'skill_chart_type' not in st.session_state:
        st.session_state.skill_chart_type = "total" # 기본값 설정
    # 그래프에서 클릭된 스킬 목록
    if 'clicked_skills' not in st.session_state:
        st.session_state.clicked_skills = []


    # 앱 제목 표시
    st.title("🚀 IT 채용정보 분석")

# --- 사이드바 렌더링 함수 ---
def render_sidebar(data):
    st.sidebar.title("💻 검색 옵션")

    # 키워드 검색 입력창
    st.sidebar.subheader("🔍 키워드 검색")
    search_term = st.sidebar.text_input("검색어 입력 (회사명, 직무, 기술스택)")

    # 회사 선택 셀렉트 박스
    # data['total']이 None이 아닐 경우에만 회사 목록 생성
    all_companies = ["전체"]
    if data['total'] is not None:
        all_companies += sorted(data['total']["company"].unique().tolist())
    selected_company = st.sidebar.selectbox("회사 선택", all_companies)

    # 기술 스택 멀티셀렉트 (사이드바 필터용)
    # 공통 기술 스택 목록 (예시) - 필요시 더 추가하거나 동적으로 생성 가능
    common_skills = [
        "Java", "Python", "JavaScript", "React", "Spring",
        "AWS", "TypeScript", "Docker", "SQL", "HTML", "CSS", "Node.js",
        "Vue.js", "Angular", "Docker", "Kubernetes", "SQL", "MySQL", "PostgreSQL",
        "MongoDB", "Redis", "Git", "CI/CD", "Agile", "Scrum", "REST API"
    ]
    # data['total']의 skill 컬럼에서 추출하여 사용성을 높일 수도 있습니다.
    # 예: all_possible_skills = sorted({s.strip() for skill_list in data['total']['skill'].dropna() for s in skill_list.split(',')}) if data['total'] is not None else []
    # selected_skills = st.sidebar.multiselect("기술 스택 선택", all_possible_skills)
    selected_skills = st.sidebar.multiselect("기술 스택 선택", common_skills)


    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 IT 채용정보 분석 대시보드")

    return search_term, selected_company, selected_skills

# --- 데이터 필터링 함수 ---
def filter_data(df, search_term, selected_company, selected_skills):
    """
    주어진 데이터프레임을 검색어, 회사, 선택된 기술 스택 기준으로 필터링합니다.

    Args:
        df: 필터링할 원본 데이터프레임.
        search_term: 키워드 검색어.
        selected_company: 선택된 회사 이름 ("전체" 포함).
        selected_skills: 선택된 기술 스택 목록 (리스트).

    Returns:
        필터링된 데이터프레임.
    """
    filtered_df = df.copy()

    # 키워드 검색어로 필터링 (회사명, 직무, 기술스택 컬럼에서 검색)
    if search_term:
        # 대소문자 구분 없이 검색, NaN 값은 False 처리
        search_mask = (
            filtered_df["company"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["position"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered_df["skill"].astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]

    # 선택한 회사로 필터링
    if selected_company != "전체":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]

    # 선택한 기술 스택으로 필터링 (선택된 모든 스킬을 포함하는 공고)
    if selected_skills:
        # 각 선택된 스킬에 대해 데이터프레임이 해당 스킬을 포함하는지 확인하며 필터링
        for skill in selected_skills:
            # 기술 스택 컬럼이 문자열이고, 해당 스킬 문자열을 포함하는지 확인
            # 대소문자 구분 없이 검색
            filtered_df = filtered_df[
                filtered_df["skill"].astype(str).str.contains(skill, case=False, na=False)
            ]

    return filtered_df

# --- 요약 정보 렌더링 함수 ---
def render_summary_metrics(filtered_df):
    st.header("📈 채용정보 요약")

    # KPI 지표를 3개 컬럼으로 나눠 표시
    col1, col2, col3 = st.columns(3)

    with col1:
        # 데이터프레임이 비어있을 경우 0으로 표시
        total_jobs = len(filtered_df) if filtered_df is not None else 0
        st.metric(label="총 채용공고 수", value=f"{total_jobs:,}")

    with col2:
        # 데이터프레임이 비어있을 경우 0으로 표시
        company_count = filtered_df["company"].nunique() if filtered_df is not None and "company" in filtered_df.columns else 0
        st.metric(label="기업 수", value=f"{company_count:,}")

    with col3:
        # 데이터프레임이 비어있을 경우 0으로 표시
        job_count = filtered_df["position"].nunique() if filtered_df is not None and "position" in filtered_df.columns else 0
        st.metric(label="고유 직무 수", value=f"{job_count:,}")

# --- 기술 스택 분석 섹션 렌더링 함수 ---
def render_skill_analysis(data, filtered_df):
    """기술 스택 분석 섹션 렌더링 (버튼 전환 애니메이션 그래프 및 클릭 이벤트)"""
    st.subheader("기술 스택 분석")

    # --- CSS 주입: 버튼 간 간격 및 크기 조절 ---
    # 주의: 이 방식은 Streamlit 내부 구조에 의존하므로, 향후 Streamlit 업데이트 시 작동이 중단될 수 있습니다.
    # unsafe_allow_html=True 사용에 유의하십시오.
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button {
        margin-right: 8px; /* 오른쪽 마진 (버튼 간 간격) */
        padding: 0px 8px; /* 상하px, 좌우px (버튼 크기 조절) */
    }
    div[data-testid="stHorizontalBlock"] button:last-child {
        margin-right: 0px;
    }
    </style>
    """, unsafe_allow_html=True)
    # --- CSS 주입 끝 ---


    # 현재 선택된 기술 스택 종류를 추적하는 세션 상태
    # 'skill_chart_type' 세션 상태는 setup_page에서 초기화됩니다.

    # 버튼 클릭 처리를 위한 함수 (세션 상태만 업데이트)
    def set_skill_chart_type(chart_type):
        st.session_state.skill_chart_type = chart_type
        # 버튼 클릭 시 상태가 변경되므로 자동 rerun 발생

    # 버튼 생성을 위한 컬럼 설정 (간격 조절 및 왼쪽 정렬)
    # 예를 들어 [1, 1, 1, 5]는 전체 너비를 8등분하여 앞의 3개 컬럼에 각각 1/8씩 할당하고,
    # 마지막 컬럼에 5/8를 할당하여 버튼들을 왼쪽에 모으는 효과를 줍니다.
    btn_col1, btn_col2, btn_col3, spacer_col = st.columns([0.8, 1, 2, 10])

    with btn_col1:
        # 버튼 클릭 시 set_skill_chart_type 함수 호출
        if st.button("전체", key="btn_total_skill"):
            set_skill_chart_type("total")
    with btn_col2:
        if st.button("백엔드", key="btn_backend_skill"):
            set_skill_chart_type("backend")
    with btn_col3:
        if st.button("프론트엔드", key="btn_frontend_skill"):
            set_skill_chart_type("frontend")
    # spacer_col은 비워두어 버튼들을 왼쪽으로 밀어냅니다.

    # 선택된 타입에 따라 데이터 소스 및 그래프 제목 설정
    current_type = st.session_state.skill_chart_type
    source_df = pd.DataFrame() # 데이터프레임 초기화 (데이터 없을 경우 사용)
    title = ""

    # 선택된 타입에 맞는 데이터 로드 (load_all_data에서 이미 캐시됨)
    if current_type == "total":
        source_df = filtered_df # '전체'는 사이드바 필터가 적용된 데이터 사용
        title = "전체 기술 스택 상위 15개"
    elif current_type == "backend":
        if data['backend'] is not None:
            source_df = data['backend'] # '백엔드'는 전체 백엔드 데이터 사용
            title = "백엔드 기술 스택 상위 15개"
        else:
            st.info("백엔드 데이터 파일을 찾을 수 없어 기술 스택 분석을 표시할 수 없습니다.")
            source_df = pd.DataFrame() # 데이터 없음을 명시
    elif current_type == "frontend":
        if data['frontend'] is not None:
            source_df = data['frontend'] # '프론트엔드'는 전체 프론트엔드 데이터 사용
            title = "프론트엔드 기술 스택 상위 15개"
        else:
            st.info("프론트엔드 데이터 파일을 찾을 수 없어 기술 스택 분석을 표시할 수 없습니다.")
            source_df = pd.DataFrame() # 데이터 없음을 명시


    # 데이터 소스가 유효하고 비어있지 않은 경우에만 그래프 생성 및 표시
    if source_df is not None and not source_df.empty:
        # 기술 스택 빈도 계산
        skill_counts = count_skills(source_df)

        # 그래프를 위한 데이터 준비 (상위 15개 스킬)
        # 빈도 계산 결과가 비어있지 않은 경우에만 처리
        if not skill_counts.empty:
            skill_df = skill_counts.head(15).reset_index()
            skill_df.columns = ["skill", "count"]

            # 애니메이션 막대 그래프 생성 (항상 세로 방향으로 가정)
            chart_orientation = "v" # 기술 스택 분석 그래프는 세로 막대

            fig = create_animated_bar_chart(
                skill_df,
                x_col="skill",
                y_col="count",
                title=title,
                orientation=chart_orientation,
                color_scale="Viridis"
            )

            # --- 그래프 표시 및 클릭 이벤트 처리 ---
            # plotly_events를 사용하여 Plotly 그래프를 렌더링하고 클릭 이벤트를 감지합니다.
            # key는 Streamlit rerun 시 widget의 상태를 유지하기 위해 고유해야 합니다.
            graph_key = f"skill_chart_{current_type}_{st.session_state.render_id}"
            clicked = plotly_events(
                fig,
                click_event=True, # 클릭 이벤트 활성화
                key=graph_key, # 고유 키 지정
                override_height=600, # 그래프 높이 고정 (px)
                # override_width 설정은 필요에 따라 추가 가능
            )

            # 클릭 이벤트 데이터 처리를 분리된 함수에게 위임 (세션 상태 업데이트 및 필요시 rerun)
            # handle_chart_click 함수는 클릭 데이터가 있을 때만 세션 상태를 변경하고 rerun을 트리거합니다.
            # 이 함수는 클릭 데이터가 없으면 아무것도 하지 않습니다.
            handle_chart_click(clicked, orientation=chart_orientation)

            # --- 클릭된 스킬 표시 ---
            # 클릭된 스킬 목록을 표시하는 함수를 호출합니다.
            # 이 함수는 세션 상태를 확인하여 목록이 비어있지 않을 때만 UI를 렌더링합니다.
            with st.container(): # 클릭된 스킬 표시를 위한 컨테이너
                display_clicked_skills(current_type) # 분리된 함수 호출

            # --- 클릭된 스킬 표시 끝 ---

        else:
            st.info("선택된 조건에 해당하는 기술 스택 데이터에서 유의미한 스킬을 찾을 수 없습니다.")
    elif source_df is not None and source_df.empty:
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")
    # source_df가 None인 경우는 위에서 이미 st.info 메시지를 출력함


# --- 직무 분석 섹션 렌더링 함수 ---
def render_job_analysis(filtered_df):
    """직무 분석 섹션 렌더링 (애니메이션 막대 그래프)"""
    st.subheader("상위 20개 직무")

    # 직무명 통합
    position_mapping = {
        r'\b(백엔드 엔지니어|Backend Engineer|Back-end Engineer)\b': '백엔드 개발자',
        r'\b(프론트엔드 엔지니어|Frontend Engineer|Front-end Engineer)\b': '프론트엔드 개발자',
        r'\b(DevOps Engineer|데브옵스 엔지니어)\b': 'DevOps 엔지니어',
        r'\bSoftware Engineer\b': '소프트웨어 엔지니어'
    }
    for pattern, replacement in position_mapping.items():
        filtered_df['position'] = filtered_df['position'].str.replace(pattern, replacement, case=False, regex=True)

    # 직무명(position) 열의 상위 빈도 항목 계산
    # 데이터프레임이 비어있지 않은 경우에만 처리
    if filtered_df is not None and not filtered_df.empty:
        position_counts = filtered_df["position"].value_counts().head(20).reset_index()
        position_counts.columns = ["position", "count"]

        # 상위 직무 데이터가 비어있지 않은 경우 그래프 생성
        if not position_counts.empty:
            fig = create_animated_bar_chart(
                position_counts,
                x_col="position", # 직무 이름
                y_col="count", # 빈도
                title="", # 섹션 제목이 있으므로 그래프 제목은 비워둠
                orientation="h", # 직무명은 길이가 길 수 있으므로 가로 막대 그래프 사용
                color_scale="Viridis" # 색상 스케일
            )
            # st.plotly_chart로 그래프 표시 (클릭 이벤트 없음)
            if fig: # create_animated_bar_chart가 None을 반환하지 않았을 경우만 표시
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("필터링된 데이터에서 상위 직무를 찾을 수 없습니다.")
    elif filtered_df is not None and filtered_df.empty:
        st.info("필터링된 데이터가 없습니다.")
    # filtered_df가 None인 경우는 main 함수에서 이미 처리됨


# --- 기업 분석 섹션 렌더링 함수 ---
def render_company_analysis(filtered_df):
    """기업 분석 섹션 렌더링 (애니메이션 막대 그래프)"""
    st.subheader("채용공고가 많은 상위 20개 기업")

    # 전체 기업 채용 공고 수 계산 (상위 20개)
    # 데이터프레임이 비어있지 않은 경우에만 처리
    if filtered_df is not None and not filtered_df.empty:
        company_counts = filtered_df["company"].value_counts().head(20).reset_index()
        company_counts.columns = ["company", "count"]

        # 상위 기업 데이터가 비어있지 않은 경우 그래프 생성
        if not company_counts.empty:
            fig = create_animated_bar_chart(
                company_counts,
                x_col="company", # 기업 이름
                y_col="count", # 빈도
                title="", # 섹션 제목이 있으므로 그래프 제목은 비워둠
                orientation="v", # 기업 수는 세로 막대가 적합
                color_scale="Plasma" # 색상 스케일
            )
            # st.plotly_chart로 그래프 표시 (클릭 이벤트 없음)
            if fig: # create_animated_bar_chart가 None을 반환하지 않았을 경우만 표시
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("필터링된 데이터에서 상위 기업을 찾을 수 없습니다.")
    elif filtered_df is not None and filtered_df.empty:
        st.info("필터링된 데이터가 없습니다.")
    # filtered_df가 None인 경우는 main 함수에서 이미 처리됨


# --- 데이터 테이블 섹션 렌더링 함수 ---
def render_data_table(filtered_df):
    """데이터 테이블 섹션 렌더링 (페이지네이션 포함)"""
    st.subheader("데이터 테이블")

    # 데이터프레임이 유효하고 비어있지 않은 경우에만 테이블 표시 및 페이지네이션 컨트롤 렌더링
    if filtered_df is not None and not filtered_df.empty:
        # 페이지네이션을 위한 페이지 크기 선택
        page_size = st.selectbox("페이지 크기", [10, 25, 50, 100], key="data_table_page_size") # 고유 키 지정

        # 총 페이지 수 계산
        total_rows = len(filtered_df)
        total_pages = (total_rows + page_size - 1) // page_size # 올림 계산

        # 현재 페이지 번호 입력
        page_number = st.number_input(
            "페이지 번호",
            min_value=1,
            max_value=max(1, total_pages), # 데이터가 없거나 1페이지 미만일 경우 min_value와 일치
            value=st.session_state.get('data_table_page', 1), # 세션 상태에서 페이지 번호 가져오기 (초기값 1)
            key="data_table_page_input" # 고유 키 지정
        )
        # 페이지 번호가 변경되면 세션 상태에 저장
        st.session_state['data_table_page'] = page_number

        # 현재 페이지 데이터 범위 계산
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)

        # 표시할 데이터프레임 슬라이싱
        display_df = filtered_df.iloc[start_idx:end_idx]

        # 데이터 정보 표시
        st.write(
            f"전체 {total_rows:,}개 중 {start_idx+1:,}~{end_idx:,}개 데이터를 표시합니다."
        )
        # 데이터프레임 표시
        st.dataframe(display_df)

    elif filtered_df is not None and filtered_df.empty:
        st.info("필터링된 데이터가 없습니다.")
    # filtered_df가 None인 경우는 main 함수에서 이미 처리됨

def render_youtube_search(search_term):
    st.subheader("YouTube 검색 결과")
    results = yt.search_youtube(YOUR_YOUTUBE_API_KEY, f'{search_term} Tutorial', 3)
    if results:
        for video in results:
            # 레이아웃을 두 개의 열로 나눔
            col1, col2 = st.columns([1, 3])  # 첫 번째 열은 썸네일, 두 번째 열은 텍스트

            with col1:
                # 썸네일 URL 생성
                thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/0.jpg"
                # 썸네일을 클릭하면 동영상 링크로 이동하도록 HTML 생성
                video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                st.markdown(
                    f'<a href="{video_url}" target="_blank">'
                    f'<img src="{thumbnail_url}" alt="YouTube Video" style="width:100%; max-width:300px;">'
                    f'</a>',
                    unsafe_allow_html=True
                )

            with col2:
                # 동영상 제목과 설명 출력
                st.write(f"**제목:** {video['title']}")
                st.write(f"**설명:** {video['description']}")

            # 구분선 추가
            st.markdown("---")