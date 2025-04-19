import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import pandas as pd
import streamlit.components.v1 as components
import urllib.parse
import os

# 고용24 오픈 API 기본 URL
BASE_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"


def fetch_employment24_data(keyword, max_pages=7):
    api_key = os.getenv("YOUR_WORK24_API_KEY", "")
    
    """
    고용24 API를 호출하여 훈련과정 정보를 가져옵니다.
    """
    if not api_key:
        st.warning("고용24 API 키가 입력되지 않았습니다. 사이드바에서 API 키를 입력해주세요.")
        return []
    
    # 키워드가 없으면 빈 결과 반환
    if not keyword:
        return []
    
    # 검색어 준비
    keyword_lower = keyword.lower()
    
    # 날짜 범위 설정
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    one_year_later = today + timedelta(days=365)
    start_date_filter = tomorrow.strftime("%Y%m%d")
    end_date_filter = one_year_later.strftime("%Y%m%d")
    
    # API 호출을 위한 파라미터 설정
    params = {
        "authKey": api_key,
        "returnType": "XML",
        "outType": '1',
        "pageSize": '100',
        "srchNcs1": '20',
        "crseTracseSe": "C0061",
        "srchTraStDt": start_date_filter,
        "srchTraEndDt": end_date_filter,
        "sort": "ASC",
        "sortCol": "TRNG_BGDE",
    }
    
    with st.spinner("고용24 데이터를 불러오는 중..."):
        all_fetched_items = []
        
        pageNum = 1
        progress_bar = st.progress(0)
        
        try:
            while pageNum <= max_pages:
                params['pageNum'] = str(pageNum)
                
                response = requests.get(BASE_URL, params=params)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                
                # 총 결과 수 (첫 페이지에서만 확인)
                if pageNum == 1:
                    scn_cnt_element = root.find('.//scn_cnt')
                    total_results = int(scn_cnt_element.text) if scn_cnt_element is not None and scn_cnt_element.text.isdigit() else 0
                    if total_results == 0:
                        st.warning("API 호출 결과가 없습니다. 검색 조건을 다시 확인하세요.")
                        return []
                
                # 현재 페이지의 아이템 목록 찾기
                current_page_items = root.findall('.//srchList/scn_list')
                all_fetched_items.extend(current_page_items)
                
                # 진행 상황 업데이트
                progress_percentage = min(pageNum / max_pages, 1.0)
                progress_bar.progress(progress_percentage)
                
                # 다음 페이지가 있는지 확인
                if len(current_page_items) < int(params['pageSize']):
                    break
                
                pageNum += 1
            
            progress_bar.progress(1.0)
            progress_bar.empty()  # ✅ 진행바 제거!
            
            # 키워드 필터링
            keyword_filtered_items = []
            for item in all_fetched_items:
                trainning_nm_element = item.find('title')
                trainning_nm = trainning_nm_element.text if trainning_nm_element is not None else ""
                
                if keyword_lower in trainning_nm.lower():
                    keyword_filtered_items.append(item)
            
            # 중복 제거 및 종료일자 기준 선택
            unique_trainings = {}
            
            for item in keyword_filtered_items:
                # 상세 정보 추출
                trainning_nm_element = item.find('title')
                inst_nm_element = item.find('subTitle')
                end_dt_element = item.find('traEndDate')
                
                trainning_nm = trainning_nm_element.text.strip() if trainning_nm_element is not None and trainning_nm_element.text else "정보 없음"
                inst_nm = inst_nm_element.text.strip() if inst_nm_element is not None and inst_nm_element.text else "정보 없음"
                end_dt_str = end_dt_element.text.strip() if end_dt_element is not None and end_dt_element.text else None
                
                # 중복 판단 기준 키 생성
                duplicate_key = (trainning_nm.lower(), inst_nm.lower())
                
                # 종료일자 파싱 시도
                current_end_date = None
                if end_dt_str:
                    try:
                        current_end_date = datetime.strptime(end_dt_str, "%Y%m%d")
                    except (ValueError, TypeError):
                        pass
                
                # 중복 관리
                if duplicate_key not in unique_trainings:
                    unique_trainings[duplicate_key] = {'item': item, 'end_date': current_end_date}
                else:
                    stored_info = unique_trainings[duplicate_key]
                    stored_end_date = stored_info['end_date']
                    
                    if (current_end_date is not None) and \
                        (stored_end_date is None or current_end_date > stored_end_date):
                        unique_trainings[duplicate_key] = {'item': item, 'end_date': current_end_date}
            
            final_trainings_list = [info['item'] for info in unique_trainings.values()]
            
            # 훈련 시작일자 기준으로 내림차순 정렬
            def get_start_date(item_element):
                start_dt_element = item_element.find('traStartDate')
                start_dt_str = start_dt_element.text.strip() if start_dt_element is not None and start_dt_element.text else None
                if start_dt_str:
                    try:
                        return datetime.strptime(start_dt_str, "%Y%m%d")
                    except (ValueError, TypeError):
                        pass
                return datetime.min
            
            final_trainings_list.sort(key=get_start_date, reverse=True)
            
            # 훈련과정 정보 추출
            result_list = []
            for item in final_trainings_list:
                training_nm_element = item.find('title')
                inst_nm_element = item.find('subTitle')
                bgng_dt_element = item.find('traStartDate')
                end_dt_element = item.find('traEndDate')
                lctn_nm_element = item.find('address')
                
                training_nm = training_nm_element.text.strip() if training_nm_element is not None and training_nm_element.text else "정보 없음"
                inst_nm = inst_nm_element.text.strip() if inst_nm_element is not None and inst_nm_element.text else "정보 없음"
                bgng_dt = bgng_dt_element.text.strip() if bgng_dt_element is not None and bgng_dt_element.text else "정보 없음"
                end_dt = end_dt_element.text.strip() if end_dt_element is not None and end_dt_element.text else "정보 없음"
                lctn_nm = lctn_nm_element.text.strip() if lctn_nm_element is not None and lctn_nm_element.text else "정보 없음"
                
                # 날짜 형식 변환
                formatted_bgng_dt = bgng_dt
                formatted_end_dt = end_dt
                if bgng_dt != "정보 없음":
                    try:
                        formatted_bgng_dt = datetime.strptime(bgng_dt, "%Y%m%d").strftime("%Y-%m-%d")
                    except ValueError:
                        pass
                
                if end_dt != "정보 없음":
                    try:
                        formatted_end_dt = datetime.strptime(end_dt, "%Y%m%d").strftime("%Y-%m-%d")
                    except ValueError:
                        pass
                
                result_list.append({
                    "과정명": training_nm,
                    "기관명": inst_nm,
                    "시작일": formatted_bgng_dt,
                    "종료일": formatted_end_dt,
                    "소재지": lctn_nm
                })
            
            return result_list
            
        except requests.exceptions.RequestException as e:
            st.error(f"API 호출 중 오류 발생: {e}")
        except ET.ParseError as e:
            st.error(f"API 응답 파싱 중 오류 발생: {e}")
        except Exception as e:
            st.error(f"예기치 않은 오류 발생: {e}")
        
        return []

# web_search_work24.py 파일의 render_employment24_results_table 함수를 수정합니다

# 검색어를 고용24에서 새 탭으로 열 수 있는 버튼 추가
def make_work24_search_url(keyword):
    once = urllib.parse.quote(keyword)
    twice = urllib.parse.quote(once)
    return (
        f"https://www.work24.go.kr/cm/f/c/0100/selectUnifySearch.do?"
        f"topQuerySearchArea=training&"  # ✅ 훈련탭 고정!
        f"topQueryData={twice}&"
        f"startDate=&endDate=&sortField=&reQuery=&matchedQuery=&includedQuery=&excludedQuery=&"
        f"startCount=1&listCount=20&reportSort=TITLE&workinfoSort=RANK&residentSort=RANK&"
        f"policySort=RANK&newsSort=RANK&bizinfoSort=RANK&trainingSort=RANK&"
        f"jobCourseSort=RANK&qualSort=RANK&etcSort=RANK"
    )
def render_employment24_results_table(results, keyword):
    """
    고용24 훈련과정 검색 결과를 표 형태로 표시합니다.
    과정명에 고용24 메인 페이지로 연결되는 링크를 제공합니다.
    """
    if not results:
        st.info(f"'{keyword}' 키워드로 검색된 훈련과정이 없습니다.")
        return
    
    st.write(f"**'{keyword}' 키워드로 검색된 훈련과정 ({len(results)}개)**")
    search_url = make_work24_search_url(keyword)
    components.html(f"""
    <button onclick="window.open('{search_url}', '_blank')"
            style="margin-top: 10px; padding: 8px 16px; font-size: 16px; background-color: #4CAF50; color: white; border: none; border-radius: 5px;">
        🔗 고용24에서 "{keyword}" 검색 결과 보기
    </button>
    """, height=60)
    
    # 결과를 데이터프레임으로 변환
    import pandas as pd
    df = pd.DataFrame(results)
    
    # 과정명에 링크 추가
    if '과정명' in df.columns:
        # 고용24 메인 페이지 URL
        main_url = "https://www.work24.go.kr"
        df['과정명_링크'] = df['과정명'].apply(
            lambda x: f'<a href="{main_url}" target="_blank">{x}</a>'
        )

        # 열 순서 재정렬 (과정명_링크를 과정명 위치에 배치)
        cols = df.columns.tolist()
        cols.remove('과정명_링크')
        cols.remove('과정명')
        cols.insert(cols.index('기관명') if '기관명' in cols else 0, '과정명_링크')
        
        # 새 데이터프레임 생성
        df_display = df[cols]
        # 열 이름 변경
        df_display = df_display.rename(columns={'과정명_링크': '과정명'})
    else:
        df_display = df
    
    # HTML 링크가 작동하도록 unsafe_allow_html=True 설정
    st.write(
    df_display.to_html(escape=False).replace(
        "<th>", '<th style="text-align: center;">'
    ),
    unsafe_allow_html=True
)

def render_clicked_skills_training():
    """
    클릭된 기술 스택에 따른 고용24 훈련과정을 표시합니다.
    이 함수는 'clicked_skills'에 저장된 기술 스택을 기반으로 검색합니다.
    """
    # 클릭된 스킬 목록 확인
    clicked_skills = st.session_state.get('clicked_skills', [])
    
    if not clicked_skills:
        return
    
    # api_key 가져오기
    api_key = os.getenv("YOUR_WORK24_API_KEY", "")
    
    # 각 스킬에 대한 훈련과정 표시
    for skill in clicked_skills:
        results = fetch_employment24_data(api_key, skill)
        render_employment24_results_table(results, skill)
        st.markdown("---")  # 구분선 추가

# 세션 상태 초기화 함수
def init_employment24_session_state():
    """
    고용24 관련 세션 상태를 초기화합니다.
    """
    if 'employment24_keyword' not in st.session_state:
        st.session_state.employment24_keyword = ""
    if 'employment24_results' not in st.session_state:
        st.session_state.employment24_results = []