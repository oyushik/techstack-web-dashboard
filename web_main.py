import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from streamlit_plotly_events import plotly_events

def autopct_func(pct):
    return f"{pct:.1f}%"


def count_skills(df, exclude_skills=None):
    skill_counts = Counter()
    for index, row in df.iterrows():
        skills_str = row["skill"]
        if pd.notna(skills_str):
            skills = [skill.strip().upper() for skill in skills_str.split(",")]
            skill_counts.update(skills)

    if exclude_skills:
        exclude_skills_upper = [skill.upper() for skill in exclude_skills]
        skill_counts = {
            skill: count
            for skill, count in skill_counts.items()
            if skill not in exclude_skills_upper
        }

    return pd.Series(skill_counts).sort_values(ascending=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_csv_data(file_name):
    try:
        # 상대 경로로 시도
        file_path = f"data/{file_name}"
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.warning(f"{file_name} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return None


def load_all_data():
    data = {
        'total': load_csv_data("merged_data_total.csv"),
        'backend': load_csv_data("merged_data_backend.csv"),
        'frontend': load_csv_data("merged_data_frontend.csv")
    }
    return data

def create_animated_bar_chart(data_df, x_col, y_col, title, orientation="v", color_scale="Plasma"):

    if data_df.empty:
        return None
        
    # 애니메이션 프레임 설정 - 최적화
    animation_frames = []
    # 최대 8개 프레임으로 제한
    for i in range(1, 8):
        subset = data_df.copy()
        subset["animated_count"] = (subset[y_col] * (i / 7)).round(1)
        
        if orientation == "h":
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset["animated_count"],
                        y=subset[x_col],
                        orientation="h",
                        marker=dict(
                            color=subset["animated_count"],
                            colorscale=color_scale,
                            showscale=True,
                            colorbar=dict(title="빈도"),
                        ),
                        text=subset["animated_count"].round(0).astype(int),
                        textposition="outside",
                        hovertemplate="<b>%{y}</b><br>빈도: %{x:,}",
                    )
                ],
                name=f"frame{i}",
            )
        else:
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset[x_col],
                        y=subset["animated_count"],
                        marker=dict(
                            color=subset["animated_count"],
                            colorscale=color_scale,
                            showscale=True,
                            colorbar=dict(title="빈도"),
                        ),
                        text=subset["animated_count"].round(0).astype(int),
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>빈도: %{y:,}",
                    )
                ],
                name=f"frame{i}",
            )
        animation_frames.append(frame)

    # 처음에는 빈 값으로 시작
    empty_vals = [0] * len(data_df)
    
    # 그래프 생성
    if orientation == "h":
        fig = go.Figure(
            data=[
                go.Bar(
                    x=empty_vals,
                    y=data_df[x_col],
                    orientation="h",
                    marker=dict(
                        color=empty_vals,
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=empty_vals,
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>빈도: %{x:,}",
                )
            ],
            frames=animation_frames,
        )
        
        # x축 범위 설정 (최대값의 1.1배까지)
        xmax = max(data_df[y_col]) * 1.1
        fig.update_layout(
            xaxis_title="빈도",
            yaxis_title="",
            xaxis_range=[0, xmax],
            yaxis={"categoryorder": "total ascending"},
        )
    else:
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_df[x_col],
                    y=empty_vals,
                    marker=dict(
                        color=empty_vals,
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=empty_vals,
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>빈도: %{y:,}",
                )
            ],
            frames=animation_frames,
        )
        
        # y축 범위 설정 (최대값의 1.1배까지)
        ymax = max(data_df[y_col]) * 1.1
        fig.update_layout(
            xaxis_title="",
            yaxis_title="빈도", 
            yaxis_range=[0, ymax],
            xaxis=dict(tickangle=-45),
        )

    # 공통 레이아웃 설정
    fig.update_layout(
        title={
            "text": title,
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        height=600,
        margin=dict(l=20 if orientation == "v" else 150, r=20, t=70, b=100 if orientation == "v" else 70),
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "▶️ 그래프 표시",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 200, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 10},
                "showactive": False,
                "x": 0.5,
                "y": 1.15,
                "xanchor": "center",
                "yanchor": "top",
            }
        ],
    )

    return fig


def create_clickable_bar_chart(data_df, title, key_prefix):
    """
    클릭 가능한 막대 그래프를 생성하는 함수
    
    Args:
        data_df: skill과 count 컬럼이 있는 데이터프레임
        title: 그래프 제목
        key_prefix: 고유한 키를 만들기 위한 접두사
    """
    # 그래프 고유 키 생성
    graph_key = f"{key_prefix}_{st.session_state.render_id}"
    
    # Plotly 그래프 생성
    fig = px.bar(
        data_df,
        x="skill", 
        y="count",
        title=title,
        color="count",
        color_continuous_scale="Viridis",
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=40, r=40, t=60, b=60),
        title_x=0.5,
    )
    
    # 클릭 이벤트 처리
    clicked = plotly_events(fig, click_event=True, key=graph_key)
    
    # 클릭 이벤트 처리 로직
    if clicked:
        with st.spinner('데이터 처리 중...'):
            selected_keyword = clicked[0]['x']
            if selected_keyword not in st.session_state.selected_skills:
                st.session_state.selected_skills.append(selected_keyword)
                # render_id를 증가시켜 다음 렌더링에서 새 키를 사용
                st.session_state.render_id += 1
    
    # 선택된 스킬 표시 - 별도 컨테이너에 표시
    with st.container():
        if st.session_state.selected_skills:
            st.write("선택된 기술 스택:", ", ".join(st.session_state.selected_skills))
            
            # 선택 초기화 버튼 추가
            if st.button("선택 초기화", key=f"clear_{key_prefix}"):
                st.session_state.selected_skills = []
                st.session_state.render_id += 1
                st.rerun()


def setup_page():
    st.set_page_config(
        page_title="IT 채용정보 분석 대시보드", 
        page_icon="📊", 
        layout="wide"
    )
    
    # 세션 상태 초기화
    if 'selected_skills' not in st.session_state:
        st.session_state.selected_skills = []
    if 'render_id' not in st.session_state:
        st.session_state.render_id = 0
    
    # 앱 제목
    st.title("🚀 IT 채용정보 분석")

def render_sidebar(data):
    st.sidebar.title("💻 검색 옵션")
    
    # 필터링 옵션 추가
    st.sidebar.subheader("🔍 키워드 검색")
    search_term = st.sidebar.text_input("검색어 입력 (회사명, 직무, 기술스택)")
    
    # 회사명 필터링 옵션
    all_companies = ["전체"] + sorted(data['total']["company"].unique().tolist())
    selected_company = st.sidebar.selectbox("회사 선택", all_companies)
    
    # 기술 스택 검색 옵션
    common_skills = [
        "Java", "Python", "JavaScript", "React", "Spring", 
        "AWS", "TypeScript", "Docker", "SQL", "HTML",
    ]
    selected_skills = st.sidebar.multiselect("기술 스택 선택", common_skills)
    
    # 푸터
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 IT 채용정보 분석 대시보드")
    
    return search_term, selected_company, selected_skills


def filter_data(df, search_term, selected_company, selected_skills):
    filtered_df = df.copy()
    
    # 검색어로 필터링
    if search_term:
        search_mask = (
            filtered_df["company"].str.contains(search_term, case=False, na=False)
            | filtered_df["position"].str.contains(search_term, case=False, na=False)
            | filtered_df["skill"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # 선택한 회사로 필터링
    if selected_company != "전체":
        filtered_df = filtered_df[filtered_df["company"] == selected_company]
    
    # 선택한 기술 스택으로 필터링
    for skill in selected_skills:
        filtered_df = filtered_df[
            filtered_df["skill"].str.contains(skill, case=False, na=False)
        ]
    
    return filtered_df


def render_summary_metrics(filtered_df):
    st.header("📈 채용정보 요약")
    
    # KPI 지표를 3개 컬럼으로 나눠 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="총 채용공고 수", value=f"{len(filtered_df):,}")
    
    with col2:
        company_count = filtered_df["company"].nunique()
        st.metric(label="기업 수", value=f"{company_count:,}")
    
    with col3:
        job_count = filtered_df["position"].nunique()
        st.metric(label="고유 직무 수", value=f"{job_count:,}")


def render_company_analysis(filtered_df):
    st.subheader("채용공고가 많은 상위 20개 기업")
    
    # 전체 기업 채용 공고 수 (상위 20개)
    company_counts = filtered_df["company"].value_counts().head(20).reset_index()
    company_counts.columns = ["company", "count"]
    
    if not company_counts.empty:
        fig = create_animated_bar_chart(
            company_counts, 
            x_col="company", 
            y_col="count", 
            title="",
            orientation="v",
            color_scale="Plasma"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("필터링된 데이터가 없습니다.")


def render_job_analysis(filtered_df):
    """직무 분석 탭 렌더링"""
    st.subheader("상위 20개 직무")
    
    # 직무명(position) 열의 상위 빈도 항목 출력
    position_counts = filtered_df["position"].value_counts().head(20).reset_index()
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
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("필터링된 데이터가 없습니다.")


def render_skill_analysis(data, filtered_df):
    """기술 스택 분석 섹션 렌더링 (버튼 전환 애니메이션 그래프)"""
    st.subheader("기술 스택 분석")


    # --- CSS 주입: 버튼 간 간격 및 크기 조절 ---
    # 주의: 이 방식은 Streamlit 내부 구조에 의존하므로, 향후 Streamlit 업데이트 시 작동이 중단될 수 있습니다.
    # unsafe_allow_html=True 사용에 유의하십시오.
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button {
        margin-right: 8px; /* 오른쪽 마진 (버튼 간 간격) */
        padding: 0px 8px; /* 상하px, 좌우px (버튼 크기 조절) */
        /* 다른 크기 속성 예시: */
        /* width: 100px; */ /* 고정 너비 설정 */
        /* height: 40px; */ /* 고정 높이 설정 */
        /* font-size: 16px; */ /* 폰트 크기 조절 */
    }
    div[data-testid="stHorizontalBlock"] button:last-child {
        margin-right: 0px;
    }
    </style>
    """, unsafe_allow_html=True)
    # --- CSS 주입 끝 ---


    # 제외할 스킬 목록 정의
    excluded_skills = ["AI", "UI", "UIUX", "NATIVE", "BOOT", "API", "WEB", "SW", "PC"]

    # 현재 선택된 기술 스택 종류를 추적하는 세션 상태
    if 'skill_chart_type' not in st.session_state:
        st.session_state.skill_chart_type = "total"

    # 버튼 클릭 처리를 위한 함수
    def set_skill_chart_type(chart_type):
        st.session_state.skill_chart_type = chart_type

    # 버튼 생성을 위한 컬럼 설정 (간격 조절 및 왼쪽 정렬)
    # 예를 들어 [1, 1, 1, 5]는 전체 너비를 8등분하여 앞의 3개 컬럼에 각각 1/8씩 할당하고
    # 마지막 컬럼에 5/8를 할당하여 버튼들을 왼쪽에 모으는 효과를 줍니다.
    btn_col1, btn_col2, btn_col3, spacer_col = st.columns([0.8, 1, 2, 10])

    with btn_col1:
        if st.button("전체", key="btn_total_skill"):
            set_skill_chart_type("total")
    with btn_col2:
        if st.button("백엔드", key="btn_backend_skill"):
            set_skill_chart_type("backend")
    with btn_col3:
        if st.button("프론트엔드", key="btn_frontend_skill"):
            set_skill_chart_type("frontend")
    # spacer_col은 비워두어 버튼들을 왼쪽으로 밀어냅니다.

    # 선택된 타입에 따라 데이터 및 제목 설정
    current_type = st.session_state.skill_chart_type
    skill_df = pd.DataFrame() # 빈 데이터프레임으로 초기화
    title = ""
    source_df = None

    if current_type == "total":
        source_df = filtered_df
    elif current_type == "backend":
        if data['backend'] is not None:
            source_df = data['backend']
        else:
            st.info("백엔드 데이터 파일을 찾을 수 없습니다.")
            source_df = pd.DataFrame() # 데이터 없음을 표시
    elif current_type == "frontend":
        if data['frontend'] is not None:
            source_df = data['frontend']
        else:
            st.info("프론트엔드 데이터 파일을 찾을 수 없습니다.")
            source_df = pd.DataFrame() # 데이터 없음을 표시

    # 데이터 소스가 유효할 경우 기술 스택 카운트 및 그래프 생성
    if source_df is not None and not source_df.empty:
        skill_counts = count_skills(
            source_df, exclude_skills=excluded_skills
        )

        # 데이터 준비 (상위 15개)
        skill_df = skill_counts.head(15).reset_index()
        skill_df.columns = ["skill", "count"]

        # 애니메이션 막대 그래프 생성
        if not skill_df.empty:
            fig = create_animated_bar_chart(
                skill_df,
                x_col="skill",
                y_col="count",
                title=title,
                orientation="v",
                color_scale="Viridis"
            )

            # 그래프 표시
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("선택된 조건에 해당하는 기술 스택 데이터가 없습니다.")
    elif source_df is not None and source_df.empty:
        # source_df가 비어있는 경우 (예: 필터링 결과가 없는 전체 탭, 또는 파일 로드 실패한 백엔드/프론트엔드 탭)
        st.info("선택된 조건에 해당하는 데이터가 없습니다.")
    # else: source_df is None (파일 로드 오류 메시지는 위에서 이미 출력됨)


    # Note: 기존의 클릭 이벤트 및 개별 스킬 선택 selectbox 로직은 제거되었습니다.
    # 사이드바의 기술 스택 멀티셀렉트를 통해 전체 데이터에 대한 필터링을 활용해주세요.


def render_data_table(filtered_df):
    """데이터 테이블 탭 렌더링"""
    st.subheader("데이터 테이블")
    
    # 페이지네이션을 위한 설정
    page_size = st.selectbox("페이지 크기", [10, 25, 50, 100])
    
    if not filtered_df.empty:
        total_pages = len(filtered_df) // page_size + (
            1 if len(filtered_df) % page_size > 0 else 0
        )
        page_number = st.number_input(
            "페이지 번호", min_value=1, max_value=max(1, total_pages), value=1
        )
        
        # 현재 페이지 데이터 가져오기
        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        
        st.write(
            f"전체 {len(filtered_df)}개 중 {start_idx+1}~{end_idx}개 데이터를 표시합니다."
        )
        st.dataframe(filtered_df.iloc[start_idx:end_idx])
    else:
        st.info("필터링된 데이터가 없습니다.")


def main():
    """메인 함수"""
    # 페이지 설정
    setup_page()
    
    # 데이터 로드
    data = load_all_data()
    
    if data['total'] is not None:
        # 사이드바 렌더링
        search_term, selected_company, selected_skills = render_sidebar(data)
        
        # 필터링 적용
        filtered_df = filter_data(data['total'], search_term, selected_company, selected_skills)
        
        # 요약 정보 렌더링
        render_summary_metrics(filtered_df)
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🧩 기술 스택 분석", "🔍 직무 분석", "📊 기업 분석", "📋 데이터 테이블"]
        )
        
        # 각 탭 렌더링
        with tab1:
            render_skill_analysis(data, filtered_df)
        with tab2:
            render_job_analysis(filtered_df)
        with tab3:
            render_company_analysis(filtered_df)
        with tab4:
            render_data_table(filtered_df)
    else:
        st.error("데이터를 불러오는데 실패했습니다. 파일 경로를 확인해주세요.")


if __name__ == "__main__":
    main()