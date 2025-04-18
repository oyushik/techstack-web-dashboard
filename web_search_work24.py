import requests
import os
import sys
import xml.etree.ElementTree as ET # XML 파싱을 위해 ElementTree 임포트

# 고용24 오픈 API 기본 URL
BASE_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"

# .env에서 API 키 가져오기
api_key = os.getenv("YOUR_WORK24_API_KEY")
if not api_key:
    print(f"오류: API_KEY가 설정되지 않았습니다.")
    sys.exit(1)

# 사용자로부터 keyword 정보만 입력 받기
keyword_value = input("검색할 키워드: ")

# --------------------------------------------------

# API 요청에 사용할 파라미터 딕셔너리 생성
params = {
    "authKey": api_key,
    "returnType": "XML",
    "outType": "1",
    "sort": "DESC",      # 설정된 정렬 순서 적용
    "sortCol": "TRNG_BGDE",  # 설정된 정렬 컬럼 적용
    "keywordType": "1",
    "gb": "",
    "keyword": keyword_value
}

print("\nAPI 요청 중...")

try:
    # requests.get() 메소드를 사용하여 API 호출
    response = requests.get(BASE_URL, params=params)

    # HTTP 응답 상태 코드 확인
    if response.status_code == 200:
        print("API 호출 성공!")

        # --- XML 응답 파싱 및 결과 출력 ---
        try:
            # XML 문자열을 ElementTree 객체로 파싱
            root = ET.fromstring(response.text)

            # 검색 결과 개수 확인
            scn_cnt_element = root.find('.//scn_cnt') # scn_cnt 태그 찾기
            scn_cnt = int(scn_cnt_element.text) if scn_cnt_element is not None and scn_cnt_element.text.isdigit() else 0

            print(f"\n총 검색 결과 수: {scn_cnt}건")

            if scn_cnt > 0:
                print("--- 검색 결과 목록 (최신 10개) ---")
                search_list = root.find('.//srchList')

                if search_list is not None:
                    # --- 실제 결과 항목 태그 찾기 및 파싱 시도 ---
                    # srchList 아래의 모든 자식 태그를 확인하여 실제 항목 태그 이름을 찾습니다.
                    items_elements = list(search_list) # srchList의 모든 자식 엘리먼트 리스트

                    actual_item_tag = None
                    if items_elements:
                        # 첫 번째 자식 엘리먼트의 태그 이름을 실제 항목 태그로 간주
                        actual_item_tag = items_elements[0].tag
                        print(f"정보: 검색 결과 항목 태그는 '{actual_item_tag}'입니다.")

                        items = search_list.findall(actual_item_tag) # 발견된 실제 태그 이름으로 찾기

                        if items:
                            print(f"가져온 결과 수: {len(items)}건 (최대 {page_size}건)")
                            for i, item in enumerate(items):
                                print(f"\n--- 결과 {i+1} ---")
                                # 각 항목 태그 안의 모든 자식 태그들을 순회하며 정보를 추출하고 출력
                                for child in item:
                                    print(f"{child.tag}: {child.text}")
                            print("--------------------------")
                        else:
                            # 이 경우는 거의 없겠지만, findall이 비어있는 경우
                              print(f"'{actual_item_tag}' 태그를 찾았으나, 해당 태그로 파싱된 결과가 없습니다.")

                    else: # srchList는 있으나 자식이 없는 경우
                        print(f"총 {scn_cnt}건의 결과가 있다고 하지만, srchList 태그 내부에 결과 항목이 없습니다. XML 구조를 다시 확인해주세요.")

                else: # srchList 태그가 없는 경우
                    print(f"총 {scn_cnt}건의 결과가 있다고 하지만, 응답 XML에 srchList 태그가 없습니다. XML 구조를 다시 확인해주세요.")

            else: # scn_cnt가 0인 경우
                print("검색 조건에 맞는 결과가 없습니다. (API 기본 날짜 범위 적용)")

        except ET.ParseError as e:
            print("원본 XML 내용:")
            print(response.text) # 파싱 오류 시 원본 XML 출력
            print(f"XML 파싱 오류 발생: {e}")
        except Exception as e:
            print(f"XML 파싱 및 처리 중 예상치 못한 오류 발생: {e}")
            # print("원본 XML 내용:") # 디버깅 필요 시 주석 해제
            # print(response.text)


    else: # HTTP 상태 코드가 200이 아닌 경우
        print(f"API 호출 실패. 상태 코드: {response.status_code}")
        print("오류 응답 내용:")
        print(response.text) # 오류 메시지가 포함될 수 있습니다.

except requests.exceptions.RequestException as e:
    print(f"API 요청 중 오류 발생: {e}")
except Exception as e:
    print(f"알 수 없는 오류 발생: {e}")
