import streamlit as st
from web_load_data import load_all_data
from web_render import (setup_page, render_sidebar, filter_data, render_summary_metrics, render_skill_analysis,
                        render_job_analysis, render_company_analysis, render_data_table, render_youtube_search)

# --- 메인 함수 ---
def main():
    """
    Streamlit 애플리케이션의 메인 실행 함수.
    페이지 설정, 데이터 로드, 사이드바 렌더링, 데이터 필터링,
    그리고 각 섹션 탭 렌더링을 조정합니다.
    """
    # 페이지 기본 설정 (제목, 아이콘, 레이아웃 등)
    setup_page()

    # 필요한 모든 데이터 로드 (캐싱 적용)
    data = load_all_data()

    # 데이터 로드 성공 여부 확인
    if data is None or data['total'] is None:
        st.error("애플리케이션 실행에 필요한 데이터를 로드하지 못했습니다. 파일 경로를 확인해주세요.")
        return # 데이터 로드 실패 시 앱 실행 중단

    # 사이드바 검색 옵션 렌더링 및 사용자 입력 값 가져오기
    search_term, selected_company, selected_skills = render_sidebar(data)

    # 사이드바 설정에 따라 전체 데이터를 필터링
    # 필터링 결과는 각 렌더링 함수에 전달
    filtered_df = filter_data(data['total'], search_term, selected_company, selected_skills)

    # 필터링된 데이터의 요약 정보 표시
    render_summary_metrics(filtered_df)

    # 메인 콘텐츠 영역에 탭 생성
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🧩 기술 스택 분석", "🔍 직무 분석", "📊 기업 분석", "📋 데이터 테이블"]
    )

    # 각 탭 클릭 시 해당 섹션의 렌더링 함수 호출
    with tab1:
        # 기술 스택 분석 섹션 렌더링 (전체 데이터와 필터링된 데이터 모두 필요)
        render_skill_analysis(data, filtered_df)
    with tab2:
        # 직무 분석 섹션 렌더링 (필터링된 데이터 사용)
        render_job_analysis(filtered_df)
    with tab3:
        # 기업 분석 섹션 렌더링 (필터링된 데이터 사용)
        render_company_analysis(filtered_df)
    with tab4:
        # 데이터 테이블 섹션 렌더링 (필터링된 데이터 사용)
        render_data_table(filtered_df)

    if search_term:
        render_youtube_search(search_term)


# 스크립트 직접 실행 시 main 함수 호출
if __name__ == "__main__":
    main()