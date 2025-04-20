import streamlit as st
import pandas as pd
from web_load_data import count_skills
from web_charts import create_animated_bar_chart
from streamlit_plotly_events import plotly_events
import web_search_youtube as yt
from web_search_work24 import fetch_work24_data, render_work24_results_table

# --- 현재 활성 선택 키워드를 결정하는 함수 ---
def get_active_selection():
    """
    그래프 클릭 스킬, 사이드바 선택 스킬, 사이드바 검색 키워드 순서로 우선순위를 부여하여
    현재 활성 상태인 키워드를 반환합니다.
    """
    clicked_skills_list = st.session_state.get('clicked_skills', [])
    sb_selected_skill = st.session_state.get('sb_selected_skill', "직접 입력")
    sb_search_term = st.session_state.get('sb_search_term', "")

    if clicked_skills_list:
        # 그래프에서 클릭된 스킬이 최우선
        return clicked_skills_list[0] # 단일 선택만 처리한다고 가정
    elif sb_selected_skill and sb_selected_skill != "직접 입력":
        # 사이드바에서 특정 스킬이 선택되었으면 다음 우선순위
        return sb_selected_skill
    elif sb_search_term:
        # 사이드바에 검색어가 입력되었으면 마지막 우선순위
        return sb_search_term
    else:
        # 아무것도 선택되지 않았으면 None 반환
        return None

# --- 클릭 이벤트 핸들러 함수 ---
# 사이드바 세션 상태를 직접 수정하는 코드를 제거합니다.
def handle_chart_click(clicked_data, orientation="v"):
    """
    Plotly chart 클릭 이벤트를 처리하여 선택된 항목을 st.session_state.clicked_skills에 설정하고
    필요시 rerun을 요청합니다.
    """
    if clicked_data:
        clicked_point = clicked_data[0]
        selected_item = None

        if orientation == "h":
            selected_item = clicked_point.get('y')
        else: # orientation == "v"
            selected_item = clicked_point.get('x')

        if selected_item:
            # 이미 선택된 스킬과 동일한 스킬을 다시 클릭했는지 확인
            # 동일한 스킬을 다시 클릭했다면, 상태를 변경하지 않고 rerun을 방지
            # get_active_selection()을 사용하여 현재 활성 선택과 비교
            current_active_selection = get_active_selection()
            if current_active_selection == selected_item:
                # 이미 활성 선택된 항목과 동일하므로 아무것도 하지 않음
                pass
            else:
                # 새로운 항목이 클릭되었거나, 이전 항목과 다를 경우
                st.session_state.clicked_skills = [selected_item] # 클릭된 스킬 업데이트

                # --- 아래 두 줄을 제거합니다. Streamlit 위젯 상태 직접 수정 오류 방지 ---
                # st.session_state.sb_search_term = ""
                # st.session_state.sb_selected_skill = "직접 입력"
                # ----------------------------------------------------------------------

                # render_id 증가 및 rerun 트리거
                # clicked_skills 상태가 변경되었으므로 rerun이 필요합니다.
                if 'render_id' not in st.session_state:
                    st.session_state.render_id = 0 # 방어적 코드
                st.session_state.render_id += 1
                st.rerun()
    # 클릭 데이터가 없으면 (예: 그래프 빈 공간 클릭) clicked_skills를 변경하지 않습니다.


# --- 선택 초기화 버튼 클릭 시 호출될 콜백 함수를 새로 정의합니다. ---
def reset_selection_callback():
    """
    선택 초기화 버튼 클릭 시 호출되는 콜백 함수.
    세션 상태를 초기화합니다.
    """
    st.session_state.clicked_skills = []
    st.session_state.sb_search_term = ""
    st.session_state.sb_selected_skill = "직접 입력" # selectbox 기본값으로 되돌림

    # render_id 증가 (상태 변경으로 rerun 발생)
    # 콜백 내부에서 세션 상태 변경은 자동으로 rerun을 트리거하므로 st.rerun()은 필요 없습니다.
    if 'render_id' in st.session_state:
        st.session_state.render_id += 1


# --- 선택 초기화 버튼 및 텍스트 표시 함수를 수정합니다. ---
# 이 함수는 모든 선택 상태를 초기화하므로 그대로 둡니다.
def render_selection_info_and_reset():
    """
    현재 활성 선택 키워드를 표시하고 초기화 버튼을 렌더링합니다.
    """
    active_selection = get_active_selection()
    render_id = st.session_state.get('render_id', 0) # 키 중복 방지를 위해 사용

    if active_selection:
        st.write("➡️ **현재 선택/검색 키워드:**", active_selection)

        # 초기화 버튼
        # on_click 콜백 사용으로 변경합니다.
        button_key = f"clear_selection_{render_id}"
        st.button(
            "선택 초기화",
            key=button_key,
            on_click=reset_selection_callback # 새로 정의한 콜백 함수를 지정합니다.
        )

    # 활성 선택이 없으면 아무것도 렌더링하지 않음.


# --- 페이지 설정 함수 ---
# 이 함수는 세션 상태를 초기화하므로 그대로 둡니다.
def setup_page():
    st.set_page_config(
        page_title="IT 채용정보 분석 대시보드",
        page_icon="📊",
        layout="wide"
    )
    # 세션 상태 초기화
    if 'render_id' not in st.session_state:
        st.session_state.render_id = 0

    # 기술 스택 분석 섹션에서 현재 선택된 차트 타입
    if 'skill_chart_type' not in st.session_state:
        st.session_state.skill_chart_type = "total"

    # 그래프에서 클릭된 스킬 목록 (handle_chart_click에서 업데이트)
    if 'clicked_skills' not in st.session_state:
        st.session_state.clicked_skills = []

    # 사이드바 상태 (render_sidebar에서 관리)
    if 'sb_selected_skill' not in st.session_state:
        st.session_state.sb_selected_skill = "직접 입력"
    if 'sb_search_term' not in st.session_state:
        st.session_state.sb_search_term = ""

    st.image("data/wordcloud_TECH_STACK.png")
    st.title("🚀 IT 채용정보로 분석한 기술 스택 트렌드")


# --- 사이드바 렌더링 함수 (수정) ---
def render_sidebar(data):
    st.sidebar.title("💻 검색 옵션")
    st.sidebar.subheader("📊 검색 기준 선택")

    common_skills = ["직접 입력"]
    if data['total'] is not None and 'skill' in data['total'].columns and not data['total'].empty:
        skill_counts = data['total']['skill'].dropna().str.split(',').explode().str.strip().value_counts()
        common_skills.extend(skill_counts.head(20).index.tolist())

    # --- 사이드바 위젯 변경 시 호출될 콜백 함수들 정의 ---

    def sb_selectbox_on_change():
        """
        사이드바 selectbox 변경 시 호출되는 콜백.
        그래프 클릭으로 선택된 스킬 상태를 초기화합니다.
        """
        # selectbox 값이 변경되면, 이전의 그래프 클릭 상태를 초기화하여
        # selectbox 선택이 get_active_selection에서 우선순위를 갖도록 합니다.
        if 'clicked_skills' in st.session_state:
            st.session_state.clicked_skills = []
        # selectbox가 "직접 입력"이 아닌 다른 값으로 변경되면, 텍스트 입력창 내용도 지우는 것이
        # 사용자 경험상 자연스러울 수 있지만, get_active_selection 로직이 sb_selected_skill을 먼저 확인하므로
        # 굳이 sb_search_term을 지우지 않아도 됩니다.

    def sb_text_input_on_change():
        """
        사이드바 text_input 변경 시 호출되는 콜백.
        그래프 클릭으로 선택된 스킬 상태와 selectbox 선택 상태를 초기화합니다.
        """
        # 텍스트 입력창 값이 변경되면, 이전의 그래프 클릭 상태를 초기화합니다.
        if 'clicked_skills' in st.session_state:
            st.session_state.clicked_skills = []
        # 텍스트 입력창 값이 변경되면, selectbox 선택 상태를 "직접 입력"으로 되돌려
        # 텍스트 입력이 get_active_selection에서 우선순위를 갖도록 합니다.
        if 'sb_selected_skill' in st.session_state and st.session_state.sb_selected_skill != "직접 입력":
            st.session_state.sb_selected_skill = "직접 입력"

    # --- 위젯 렌더링 및 on_change 콜백 연결 ---

    # 대표 스킬 선택 selectbox
    # key를 통해 sb_selected_skill 세션 상태가 업데이트됩니다.
    # on_change 콜백을 추가합니다.
    st.sidebar.selectbox(
        "대표 스킬 선택",
        common_skills,
        key="sb_selected_skill",
        on_change=sb_selectbox_on_change # 콜백 함수 연결
    )

    # --- 키워드 검색 입력창 ---
    st.sidebar.subheader("🔍 키워드 검색 (직접 입력)")

    # '대표 스킬 선택'이 '직접 입력'일 때만 텍스트 입력창 활성화
    text_input_disabled = (st.session_state.get('sb_selected_skill', "직접 입력") != "직접 입력")

    # key를 통해 sb_search_term 세션 상태가 업데이트됩니다.
    # on_change 콜백을 추가합니다.
    st.sidebar.text_input(
        "검색어 입력 (스킬, 직무)",
        key="sb_search_term",
        disabled=text_input_disabled,
        placeholder="직접 검색어를 입력하세요" if not text_input_disabled else "",
        on_change=sb_text_input_on_change # 콜백 함수 연결
    )

    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 IT 채용정보 분석 대시보드")


# --- 선택된 스킬/키워드 관련 정보 렌더링 ---
# 이 함수는 get_active_selection()을 사용하여 검색어를 결정하고 render_selection_info_and_reset을 호출합니다.
def render_related_information():
    """
    get_active_selection()에 기반하여 관련 정보 (고용24, YouTube)를 렌더링합니다.
    """
    active_selection = get_active_selection()

    if active_selection:
        st.subheader(f"'{active_selection}' 관련 정보")

        # 현재 선택 정보 및 초기화 버튼 표시
        render_selection_info_and_reset()

        # Work24 검색 결과 (단일 활성 선택 키워드 사용)
        work24_results = fetch_work24_data(active_selection)
        render_work24_results_table(work24_results, active_selection)

        # YouTube 검색 결과 (단일 활성 선택 키워드 사용)
        render_youtube_search(active_selection)

        st.markdown("---")
    # 활성 선택이 없으면 아무것도 렌더링하지 않음.

# --- 요약 정보 렌더링 함수 ---
# 이 함수는 filtered_df와 get_active_selection()을 사용합니다.
def render_summary_metrics(filtered_df):
    """
    filtered_df에 기반하여 요약 정보를 렌더링합니다.
    '선택 키워드'는 get_active_selection() 결과를 사용합니다.
    """
    col1, col2, col3, spacer_col1 = st.columns(([1, 1, 1, 2]))

    active_selection = get_active_selection() # 활성 선택 키워드 가져오기

    with col1:
        display_keyword = active_selection if active_selection else "-"
        st.metric(label="선택 키워드", value=display_keyword)

    with col2:
        total_jobs = len(filtered_df) if filtered_df is not None else 0
        st.metric(label=" 관련 공고", value=f"{total_jobs:,}")

    with col3:
        company_count = filtered_df["company"].nunique() if filtered_df is not None and "company" in filtered_df.columns else 0
        st.metric(label="관련 기업", value=f"{company_count:,}")


# --- 기술 스택 분석 섹션 렌더링 함수 (수정) ---
# 차트 타입 변경 시 사이드바 세션 상태를 초기화하는 코드를 제거합니다.
def render_skill_analysis(data):
    """기술 스택 분석 섹션 렌더링 (버튼 전환 애니메이션 그래프 및 클릭 이벤트)"""
    skill_display = 20

    st.subheader(f"TOP {skill_display} 기술 스택 분석")

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button {
        margin-right: 8px;
        padding: 0px 8px;
    }
    div[data-testid="stHorizontalBlock"] button:last-child {
        margin-right: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 버튼 클릭 처리를 위한 함수 (세션 상태만 업데이트)
    def set_skill_chart_type(chart_type):
        st.session_state.skill_chart_type = chart_type
        # 차트 전환 시 이전 클릭 정보 초기화
        st.session_state.clicked_skills = []

        # render_id를 증가시켜 plotly_events 키를 갱신하고 rerun 트리거
        if 'render_id' in st.session_state:
            st.session_state.render_id += 1
        st.rerun()


    btn_col1, btn_col2, btn_col3, spacer_col = st.columns([0.8, 1, 2, 10])

    # 버튼 클릭 시 set_skill_chart_type 함수 호출
    with btn_col1:
        if st.button("전체", key="btn_total_skill"):
            set_skill_chart_type("total")
    with btn_col2:
        if st.button("백엔드", key="btn_backend_skill"):
            set_skill_chart_type("backend")
    with btn_col3:
        if st.button("프론트엔드", key="btn_frontend_skill"):
            set_skill_chart_type("frontend")

    current_type = st.session_state.skill_chart_type
    source_df = pd.DataFrame()

    # .get()을 사용하여 안전하게 데이터 접근
    if current_type == "total":
        source_df = data.get('total')
    elif current_type == "backend":
        source_df = data.get('backend')
    elif current_type == "frontend":
        source_df = data.get('frontend')


    if source_df is not None and isinstance(source_df, pd.DataFrame) and not source_df.empty:
        skill_counts = count_skills(source_df)

        if not skill_counts.empty:
            skill_df = skill_counts.head(skill_display).reset_index()
            skill_df.columns = ["skill", "count"]

            chart_orientation = "v"

            fig = create_animated_bar_chart(
                skill_df,
                x_col="skill",
                y_col="count",
                title="",
                orientation=chart_orientation,
                color_scale="Viridis"
            )

            # --- 여기에 그래프 우측 상단에 텍스트를 추가합니다. ---
            fig.update_layout(
                annotations=[
                    dict(
                        text="콘텐츠 추천을 원하는 스킬의 그래프 막대를 클릭하세요!", # 표시할 텍스트
                        xref="paper",       # x 좌표계를 'paper'로 설정 (0-1 범위)
                        yref="paper",       # y 좌표계를 'paper'로 설정 (0-1 범위)
                        x=0.5,                # x 위치: 1은 그래프의 가장 오른쪽 끝
                        y=1,                # y 위치: 1은 그래프의 가장 위쪽 끝
                        showarrow=False,    # 화살표 표시 안 함
                        xanchor="center",    # 텍스트의 오른쪽 끝을 x=1 위치에 고정
                        yanchor="top",      # 텍스트의 위쪽 끝을 y=1 위치에 고정
                        bgcolor="rgba(255, 255, 255, 0.6)", # 배경색 (선택 사항)
                        bordercolor="rgba(0,0,0,0.3)",     # 테두리 색 (선택 사항)
                        borderwidth=1,
                        borderpad=4,
                        font=dict(
                            size=16,
                            color="black"
                        )
                    )
                ]
            )
            # ----------------------------------------------------

            # 그래프 표시 및 클릭 이벤트 처리
            graph_key = f"skill_chart_{current_type}_{st.session_state.render_id}"
            clicked = plotly_events(
                fig, # 수정된 fig 객체 사용
                click_event=True,
                key=graph_key,
                override_height=600,
            )

            # 클릭 이벤트 데이터 처리를 handle_chart_click 함수에게 위임
            handle_chart_click(clicked, orientation=chart_orientation)

        else:
            st.info("선택된 조건에 해당하는 기술 스택 데이터에서 유의미한 스킬을 찾을 수 없습니다.")
    elif source_df is not None and isinstance(source_df, pd.DataFrame) and source_df.empty:
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")
    else:
        # 데이터 로드 실패 또는 None인 경우
        if current_type in ['backend', 'frontend'] and data.get(current_type) is None:
            st.info(f"{current_type.capitalize()} 데이터 파일을 찾을 수 없어 기술 스택 분석을 표시할 수 없습니다.")


# --- 직무 분석 섹션 렌더링 함수 ---
def render_job_analysis(filtered_df):
    """직무 분석 섹션 렌더링 (애니메이션 막대 그래프)"""
    job_display = 20
    st.subheader(f"TOP {job_display} 직무 분석")

    position_mapping = {
        r'\b(백엔드 엔지니어|백엔드 개발자 (5년 이상)|백엔드 개발자 (3년 이상)|시니어 백엔드 개발자|Backend Engineer|Back-end Engineer)\b': '백엔드 개발자',
        r'\b(프론트엔드 엔지니어|프론트엔드 개발자 (5년 이상)|프론트엔드 개발자 (3년 이상)|시니어 프론트엔드 개발자|Frontend Engineer|Front-end Engineer)\b': '프론트엔드 개발자',
        r'\b(DevOps Engineer|데브옵스 엔지니어)\b': 'DevOps 엔지니어',
        r'\bSoftware Engineer\b': '소프트웨어 엔지니어',
        r'\bData Engineer\b': '데이터 엔지니어',
        r'\bQA Engineer\b': 'QA 엔지니어',
        r'\b(Android Developer|Android 개발자)\b': '안드로이드 개발자',
        r'\biOS Developer\b': 'iOS 개발자'
    }
    if filtered_df is not None and not filtered_df.empty:
        temp_df = filtered_df.copy()
        temp_df['position'] = temp_df['position'].astype(str).replace(position_mapping, regex=True) # replace 사용 시 na=False는 지원 안됨. astype(str) 먼저 적용.


        position_counts = temp_df["position"].value_counts().head(job_display).reset_index()
        position_counts.columns = ["position", "count"]

        if not position_counts.empty:
            fig = create_animated_bar_chart(
                position_counts,
                x_col="position",
                y_col="count",
                title="",
                orientation="h",
                color_scale="Viridis"
            )

            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("필터링된 데이터에서 상위 직무를 찾을 수 없습니다.")
    elif filtered_df is not None and filtered_df.empty:
        st.info("필터링된 데이터가 없습니다.")


# --- 데이터 테이블 섹션 렌더링 함수 ---
def render_data_table(filtered_df):
    """데이터 테이블 섹션 렌더링 (페이지네이션 포함)"""
    st.subheader("데이터 테이블")

    if filtered_df is not None and not filtered_df.empty:
        page_size = st.selectbox("페이지 크기", [10, 25, 50, 100], key="data_table_page_size")

        total_rows = len(filtered_df)
        total_pages = (total_rows + page_size - 1) // page_size

        max_page = max(1, total_pages)
        current_page = st.session_state.get('data_table_page', 1)
        # 페이지 크기 변경 등으로 인해 현재 페이지가 유효 범위를 벗어날 경우 조정
        if current_page > max_page:
            current_page = max_page
        if current_page < 1:
            current_page = 1

        page_number = st.number_input(
            "페이지 번호",
            min_value=1,
            max_value=max_page,
            value=current_page,
            key="data_table_page_input"
        )
        st.session_state['data_table_page'] = page_number # 페이지 번호 변경 시 세션 상태 업데이트


        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)

        display_df = filtered_df.iloc[start_idx:end_idx]

        st.write(
            f"전체 {total_rows:,}개 중 {start_idx+1:,}~{end_idx:,}개 데이터를 표시합니다."
        )
        st.dataframe(display_df)

    elif filtered_df is not None and filtered_df.empty:
        st.info("필터링된 데이터가 없습니다.")


# --- YouTube 검색 결과 렌더링 함수 ---
# 이 함수는 render_related_information에서 호출됩니다.
def render_youtube_search(search_term):
    """특정 search_term에 대한 YouTube 검색 결과를 렌더링합니다."""
    st.subheader(f"YouTube '{search_term}' 검색 결과")
    results = yt.search_youtube(f'{search_term} Tutorial', 3)
    if results:
        for video in results:
            col1, col2 = st.columns([1, 3])

            with col1:
                video_id = video.get('video_id')
                # 썸네일 URL 및 비디오 URL 생성 시 video_id 유효성 검사 및 안정적인 URL 사용
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg" if video_id else ""
                video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else "#"

                if video_id:
                    st.markdown(
                        f'<a href="{video_url}" target="_blank">'
                        f'<img src="{thumbnail_url}" alt="YouTube Video Thumbnail" style="width:100%; max-width:300px; border-radius: 5px;">'
                        f'</a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.write("썸네일 로드 오류")

            with col2:
                title = video.get('title', '제목 없음')
                description = video.get('description', '설명 없음')
                st.write(f"**제목:** {title}")
                st.write(f"**설명:** {description}")

            st.markdown("---")
    else:
        st.info(f"'{search_term}'에 대한 YouTube 검색 결과를 찾을 수 없습니다.")
