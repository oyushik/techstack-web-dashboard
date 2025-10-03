import streamlit as st
from src.dashboard.data_loader import load_all_data, filter_data
from src.dashboard.renderer import (
    setup_page,
    render_sidebar,
    render_summary_metrics,
    render_skill_analysis,
    render_job_analysis,
    render_data_table,
    render_related_information
)

def main():
    """
    Streamlit 애플리케이션의 메인 실행 함수.
    페이지 설정, 데이터 로드, 사이드바 렌더링, 데이터 필터링,
    요약 정보, 탭, 관련 정보 섹션 렌더링을 조정합니다.
    """
    # 페이지 기본 설정 (제목, 아이콘, 레이아웃 등)
    setup_page()

    # 필요한 모든 데이터 로드 (캐싱 적용)
    data = load_all_data()

    # 데이터 로드 성공 여부 확인
    if data is None or data.get('total') is None: # .get()을 사용하여 키 부재 시 오류 방지
        st.error("애플리케이션 실행에 필요한 데이터를 로드하지 못했습니다. 데이터 로드 함수(load_all_data) 또는 파일 경로를 확인해주세요.")
        return

    # 사이드바 검색 옵션 렌더링.
    # render_sidebar 함수는 이제 값을 반환하지 않고, 세션 상태(sb_search_term, sb_selected_skill)를 직접 업데이트합니다.
    render_sidebar(data)

    # 사이드바 세션 상태에서 현재 검색/선택 값을 가져와서 데이터 필터링에 사용합니다.
    # 필터링 로직은 사이드바 입력/선택에만 기반하며, 그래프 클릭 상태(clicked_skills)에는 영향을 받지 않습니다.
    current_sb_search_term = st.session_state.get('sb_search_term', '')
    current_sb_selected_skill = st.session_state.get('sb_selected_skill', '직접 입력')

    # 사이드바 설정에 따라 전체 데이터를 필터링
    # filter_data 함수는 여전히 검색어와 선택 스킬을 인자로 받습니다.
    # web_load_data.py의 filter_data 함수 구현이 이 인자들을 사용하도록 되어 있어야 합니다.
    filtered_df = filter_data(data.get('total'), current_sb_search_term, current_sb_selected_skill)


    # 필터링된 데이터 요약 정보 표시
    render_summary_metrics(filtered_df)

    # 메인 콘텐츠 영역에 탭 생성
    # 이 시점에서 탭 선택창이 UI에 나타납니다.
    tab1, tab2, tab3 = st.tabs(
        ["🧩 기술 스택 분석", "🔍 직무 분석", "📋 데이터 테이블"]
    )

    # 각 탭 클릭 시 해당 섹션의 렌더링 함수 호출
    # 이 함수들은 사용자가 탭을 클릭할 때 해당 탭 내용이 렌더링되도록 합니다.
    with tab1:
        # 검색 정보를 탭 안에, 그래프보다 위에 표시
        render_related_information()
        render_skill_analysis(data)

    with tab2:
        render_job_analysis(filtered_df)

    with tab3:
        render_data_table(filtered_df)


if __name__ == "__main__":
    main()