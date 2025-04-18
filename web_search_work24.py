import requests
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# 고용24 오픈 API 기본 URL
BASE_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"

# .env에서 API 키 가져오기
api_key = os.getenv("YOUR_WORK24_API_KEY")
if not api_key:
    print(f"오류: YOUR_WORK24_API_KEY 환경 변수가 설정되지 않았습니다.")
    print(f"스크립트 실행 전 환경 변수 설정을 확인하거나 .env 파일을 사용하세요.")
    sys.exit(1)

# 사용자로부터 keyword 정보 입력 받기
keyword_value = input("검색할 키워드: ")
# 대소문자 구분 없이 비교하기 위해 입력 키워드를 소문자로 변환
keyword_lower = keyword_value.lower()

print(f"\n키워드 '{keyword_value}'와 관련된 훈련과정을 검색합니다.")

# '최신' 기준을 위해 오늘 날짜부터 1년 후까지의 기간 설정 및 시작일자 내림차순 정렬 후 formatting
today = datetime.now()
tomorrow = today + timedelta(days=1) # 오늘 날짜에 1일 더하기
one_year_later = today + timedelta(days=365)
start_date_filter = tomorrow.strftime("%Y%m%d")
end_date_filter = one_year_later.strftime("%Y%m%d")

# API 호출을 위한 파라미터 설정 (페이지 번호는 루프 안에서 업데이트)
params = {
    "authKey": api_key,          # 필수: API 키
    "returnType": "XML",         # 응답 형식
    "outType": '1',              # 임의 지정했던 파라미터 (API 명세에 따라 확인 필요)
    "pageSize": '100',           # 페이지당 결과 수 (API 제한 100 반영)
    "srchNcs1": '20',
    "crseTracseSe": "C0061",
    "srchTraStDt": start_date_filter, # 훈련 시작일자 검색 시작 범위
    "srchTraEndDt": end_date_filter,  # 훈련 시작일자 검색 종료 범위
    "sort": "ASC",              # 정렬 방향 (내림차순)
    "sortCol": "TRNG_BGDE",      # 정렬 기준 (훈련 시작일자)
}

# 모든 페이지에서 가져온 원본 아이템
all_fetched_items = []

pageNum = 1
max_pages_to_fetch = 7 # 안전을 위한 최대 페이지 수 제한 (조정 가능)
# API의 실제 총 결과 수(scn_cnt)를 이용해 total_pages를 계산하고 루프 조건을 scn_cnt 기준으로 하는 것이 더 정확합니다.

print(f"설정된 검색 기간: {start_date_filter} ~ {end_date_filter}")
print(f"페이지당 가져올 결과 수: {params['pageSize']}")

try:
    while pageNum <= max_pages_to_fetch: # 최대 페이지 제한
        print(f"\nFetching page {pageNum}...")
        params['pageNum'] = str(pageNum) # 페이지 번호 파라미터 업데이트

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # HTTP 오류 확인

        root = ET.fromstring(response.text)

        # 총 결과 수 (첫 페이지에서만 참고)
        if pageNum == 1:
            scn_cnt_element = root.find('.//scn_cnt')
            total_results = int(scn_cnt_element.text) if scn_cnt_element is not None and scn_cnt_element.text.isdigit() else 0
            print(f"API에서 가져온 총 결과 수 예상 (필터링 및 중복 제거 전): {total_results}")
            if total_results == 0:
                print("API 호출 결과 목록이 비어있습니다. 검색 조건을 다시 확인하세요.")
                break # 결과가 없으면 루프 종료

        # 현재 페이지의 아이템 목록 찾기
        current_page_items = root.findall('.//srchList/scn_list')
        all_fetched_items.extend(current_page_items) # 가져온 아이템을 전체 목록에 추가

        print(f"-> Fetched {len(current_page_items)} items from page {pageNum}.")

        # 다음 페이지가 있는지 확인 (가져온 아이템 수가 pageSize보다 적으면 마지막 페이지)
        if len(current_page_items) < int(params['pageSize']):
            print(f"-> Last page ({pageNum}) reached. Stopping fetch.")
            break # 마지막 페이지이므로 루프 종료

        pageNum += 1 # 다음 페이지로 이동

    print(f"\n--- API 호출 완료. 총 {len(all_fetched_items)}개의 원본 결과 가져옴 ---")

    # --- 클라이언트 측 키워드 필터링 수행 ---
    print(f"가져온 결과 중 키워드 '{keyword_value}' 포함 과정을 필터링합니다.")
    # 필터링된 결과를 임시로 저장
    keyword_filtered_items = []
    for item in all_fetched_items:
        trainning_nm_element = item.find('title')
        trainning_nm = trainning_nm_element.text if trainning_nm_element is not None else ""

        if keyword_lower in trainning_nm.lower():
            keyword_filtered_items.append(item)

    print(f"-> 키워드 필터링 후 {len(keyword_filtered_items)}개 결과 남음.")

    # --- 중복 제거 및 종료일자 기준 선택 ---
    print("필터링된 결과에서 중복된 과정/기관 조합을 제거하고, 종료일이 가장 늦은 데이터 선택...")

    # { (과정명.lower(), 기관명.lower()): { 'item': ET.Element, 'end_date': datetime object or None } }
    unique_trainings = {}

    for item in keyword_filtered_items:
        # 상세 정보 추출 (중복 판단 및 비교에 필요한 항목)
        trainning_nm_element = item.find('title')
        inst_nm_element = item.find('subTitle')
        end_dt_element = item.find('traEndDate')

        trainning_nm = trainning_nm_element.text.strip() if trainning_nm_element is not None and trainning_nm_element.text else "정보 없음"
        inst_nm = inst_nm_element.text.strip() if inst_nm_element is not None and inst_nm_element.text else "정보 없음"
        end_dt_str = end_dt_element.text.strip() if end_dt_element is not None and end_dt_element.text else None

        # 중복 판단 기준 키 생성 (과정명과 기관명 사용, 대소문자 구분 없음)
        duplicate_key = (trainning_nm.lower(), inst_nm.lower())

        # 종료일자 파싱 시도
        current_end_date = None
        if end_dt_str:
            try:
                current_end_date = datetime.strptime(end_dt_str, "%Y%m%d")
            except (ValueError, TypeError):
                # 날짜 형식 오류 시 경고 출력 (필요하다면)
                # print(f"경고: '{trainning_nm}' 과정의 종료일자 '{end_dt_str}' 파싱 오류.")
                pass # 파싱 실패 시 None 유지

        # unique_trainings 딕셔너리 업데이트 로직
        if duplicate_key not in unique_trainings:
            # 이 조합이 처음 등장한 경우
            unique_trainings[duplicate_key] = {'item': item, 'end_date': current_end_date}
        else:
            # 이미 존재하는 조합인 경우
            stored_info = unique_trainings[duplicate_key]
            stored_end_date = stored_info['end_date']

            # 현재 아이템의 종료일자가 더 늦거나, 현재 아이템은 유효한 날짜인데 저장된 아이템은 날짜가 없는 경우
            if (current_end_date is not None) and \
                (stored_end_date is None or current_end_date > stored_end_date):
                # 현재 아이템으로 업데이트
                unique_trainings[duplicate_key] = {'item': item, 'end_date': current_end_date}
            # else: 현재 아이템의 종료일자가 저장된 아이템보다 같거나 이전이면 저장된 데이터를 유지

    # 중복 제거 및 선택이 완료된 최종 결과 리스트 추출
    final_trainings_list = [info['item'] for info in unique_trainings.values()]

    # 최종 결과를 훈련 시작일자(TRNG_BGDE) 기준으로 다시 내림차순 정렬
    # (API 호출 시 이미 정렬했으나, 중복 제거 과정에서 순서가 변경될 수 있으므로 다시 정렬)
    def get_start_date(item_element):
        start_dt_element = item_element.find('traStartDate')
        start_dt_str = start_dt_element.text.strip() if start_dt_element is not None and start_dt_element.text else None
        if start_dt_str:
            try:
                return datetime.strptime(start_dt_str, "%Y%m%d")
            except (ValueError, TypeError):
                pass
        return datetime.min # 파싱 실패 또는 정보 없음 시 가장 이른 날짜로 취급

    final_trainings_list.sort(key=get_start_date, reverse=True)

    # --- 최종 필터링된 결과 출력 ---
    if final_trainings_list:
        print(f"\n--- 최종 검색 결과 (키워드 '{keyword_value}' 포함, 중복 제거 후 {len(final_trainings_list)}개) ---")
        for item in final_trainings_list:
            # 상세 정보 추출
            inst_nm_element = item.find('subTitle')     # 기관명
            bgng_dt_element = item.find('traStartDate') # 훈련시작일
            end_dt_element = item.find('traEndDate')    # 훈련종료일
            lctn_nm_element = item.find('address')      # 소재지명
            trainning_nm_element = item.find('title')   # 과정명

            trainning_nm = trainning_nm_element.text.strip() if trainning_nm_element is not None and trainning_nm_element.text else "정보 없음"
            inst_nm = inst_nm_element.text.strip() if inst_nm_element is not None and inst_nm_element.text else "정보 없음"
            bgng_dt = bgng_dt_element.text.strip() if bgng_dt_element is not None and bgng_dt_element.text else "정보 없음"
            end_dt = end_dt_element.text.strip() if end_dt_element is not None and end_dt_element.text else "정보 없음"
            lctn_nm = lctn_nm_element.text.strip() if lctn_nm_element is not None and lctn_nm_element.text else "정보 없음"


            print(f"과정명: {trainning_nm}")
            print(f"기관명: {inst_nm}")
            print(f"기간: {bgng_dt} ~ {end_dt}")
            print(f"소재지: {lctn_nm}")
            print("-" * 20)

    else:
        print(f"\n키워드 '{keyword_value}'를 포함하며 중복 제거 후 남은 훈련과정이 없습니다.")


except requests.exceptions.RequestException as e:
    print(f"\nAPI 호출 중 오류 발생: {e}")
except ET.ParseError as e:
    print(f"\nAPI 응답 파싱 중 오류 발생 (응답이 유효한 XML 형식이 아니거나 예상과 다릅니다): {e}")
except Exception as e:
    print(f"\n예기치 않은 오류 발생: {e}")

print("\n전체 검색, 필터링 및 중복 제거가 완료되었습니다.")