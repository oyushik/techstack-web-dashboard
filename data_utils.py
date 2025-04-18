# data_utils.py

# 라이브러리 임포트
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging
import os
import re
from typing import List, Dict, Any # 타입 힌트를 위해 임포트

# 로깅 설정 함수
def setup_logging(level=logging.INFO, log_format='%(asctime)s - %(levelname)s - %(message)s'):
    """
    로깅 설정을 초기화합니다. 노트북 환경에서 재실행 시 중복 로거 생성을 방지합니다.
    """
    # 기존 핸들러 제거 (노트북에서 재실행 시 중복 로깅 방지)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=level, format=log_format)
    logging.info("로깅 설정 완료")

# 기본 요청 헤더 상수
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Wanted-Platform': 'web',
    'Wanted-Service': 'wanted',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}
logging.info("기본 헤더 설정 완료 (상수)")


# 직종 구분 URL 파라미터 생성 함수
def get_job_category_url(job_category: str = "total") -> str:
    """
    직종 카테고리 이름에 따라 Wanted 공고 검색에 사용될 URL 파라미터를 생성합니다.

    Args:
        job_category (str): 직종 카테고리 이름 ("total", "backend", "frontend" 등).
                            기본값은 "total".

    Returns:
        str: 생성된 URL 파라미터 문자열.
    """
    if job_category.lower() == "total":
        return "?jobGroup=DEVELOPER"
    elif job_category.lower() == "backend":
        return "?job=BACKEND_DEVELOPER&jobGroup=DEVELOPER"
    elif job_category.lower() == "frontend":
        return "?job=FRONTEND_DEVELOPER&jobGroup=DEVELOPER"
    else:
        logging.warning(f"알 수 없는 직종 카테고리 '{job_category}' 입니다. 기본값인 'total'을 사용합니다.")
        return "?jobGroup=DEVELOPER"

# skill 데이터 필터링 함수 정의
def filter_skill_data(skill: str | None) -> str:
    """
    skill 데이터에서 조건부로 특수문자를 제거하고, 단어 목록 형태로 정리합니다.

    Args:
        skill (str | None): 원본 스킬 문자열.

    Returns:
        str: 필터링 및 정리된 스킬 문자열 (', '로 구분된 단어 목록).
            입력이 None이거나 빈 문자열이면 빈 문자열을 반환합니다.
    """
    if not skill:
        return ""

    # 0. 한글 제거
    no_hangul = re.compile('[ㄱ-ㅣ가-힣]+')
    filtered_skill = no_hangul.sub('', skill)

    # 1. 개행 문자 제거
    filtered_skill = filtered_skill.replace('\n', '')

    # 2. LINE SEPARATOR 제거 (U+2028)
    filtered_skill = filtered_skill.replace('\u2028', '')

    # 3. 알파벳, '#', '+', 공백이 아닌 모든 문자 제거 (온점 포함)
    filtered_skill = re.sub(r"[^a-zA-Z#+\s]", "", filtered_skill)

    # 4. 알파벳 오른쪽 옆에 공백 없이 붙어 있는 숫자를 제외한 모든 숫자 제거
    def remove_standalone_numbers(text):
        def replace(match):
            return ""
        # 숫자 앞뒤로 알파벳이 없는 경우 제거
        return re.sub(r"(?<![a-zA-Z])\d+(?![a-zA-Z])", replace, text)

    filtered_skill = remove_standalone_numbers(filtered_skill)

    # 5. 단어 분리, 공백 제거, 중복 제거 및 ', '로 연결
    words = filtered_skill.split()  # 공백을 기준으로 단어 분리
    unique_words = []
    seen = set()
    for word in words:
        if word not in seen:
            unique_words.append(word)
            seen.add(word)

    filtered_skill = ', '.join(unique_words)

    return filtered_skill

# 데이터프레임을 CSV 파일로 저장하는 함수
def save_data_to_csv(data: List[Dict[str, Any]] | pd.DataFrame, filename: str, folder: str = 'data', encoding: str = 'utf-8-sig', index: bool = False):
    """
    리스트 형태의 데이터(Dict 리스트) 또는 DataFrame을 CSV 파일로 저장합니다.
    저장할 폴더가 없으면 생성합니다.

    Args:
        data (List[Dict[str, Any]] | pd.DataFrame): 저장할 데이터. Dict의 리스트 또는 pandas DataFrame.
        filename (str): 저장할 CSV 파일 이름 (예: 'my_data.csv').
        folder (str): CSV 파일을 저장할 폴더 이름. 기본값은 'data'.
        encoding (str): CSV 파일 인코딩. 기본값은 'utf-8-sig' (Excel에서 한글 깨짐 방지).
        index (bool): DataFrame 인덱스를 CSV에 쓸지 여부. 기본값은 False.

    Returns:
        str | None: 성공 시 저장된 파일의 전체 경로를 반환하고, 실패 시 None을 반환합니다.
    """
    if not data:
        logging.warning("저장할 데이터가 없습니다. CSV 파일을 생성하지 않습니다.")
        return None

    if isinstance(data, list):
        logging.info("수집된 데이터를 DataFrame으로 변환 중...")
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        logging.error(f"지원되지 않는 데이터 타입입니다: {type(data)}. Dict의 리스트 또는 DataFrame을 입력해주세요.")
        return None

    # 저장할 전체 경로 생성
    filepath = os.path.join(folder, filename)

    # 해당 폴더가 없으면 생성
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            logging.info(f"'{folder}' 폴더를 생성했습니다.")
        except OSError as e:
            logging.error(f"'{folder}' 폴더 생성 중 오류 발생: {e}", exc_info=True)
            print(f"\n폴더 생성 실패: {e}")
            return None
    else:
        logging.info(f"'{folder}' 폴더가 이미 존재합니다.")

    try:
        # encoding='utf-8-sig' : Excel에서 한글 깨짐 방지 (BOM 포함 UTF-8)
        df.to_csv(filepath, index=index, encoding=encoding)
        logging.info(f"DataFrame이 '{filepath}'으로 성공적으로 저장되었습니다.")
        print(f"\n파일 저장 완료: {filepath}")
        return filepath
    except Exception as e:
        logging.error(f"DataFrame을 CSV로 저장하는 중 오류 발생: {e}", exc_info=True)
        print(f"\n파일 저장 실패: {e}")
        return None

# CSV 파일을 읽어와 DataFrame으로 반환하는 함수
def load_data_from_csv(filepath: str, encoding: str = 'utf-8-sig') -> pd.DataFrame | None:
    """
    CSV 파일을 읽어와 pandas DataFrame으로 반환합니다.

    Args:
        filepath (str): 읽어올 CSV 파일의 전체 경로.
        encoding (str): CSV 파일 인코딩. 기본값은 'utf-8-sig'.

    Returns:
        pd.DataFrame | None: 파일 읽기에 성공하면 DataFrame을 반환하고,
                            파일이 없거나 읽기 실패 시 None을 반환합니다.
    """
    if not os.path.exists(filepath):
        logging.error(f"파일을 찾을 수 없습니다: '{filepath}'")
        print(f"\n파일을 찾을 수 없습니다: {filepath}")
        return None

    try:
        df = pd.read_csv(filepath, encoding=encoding)
        logging.info(f"'{filepath}' 파일에서 DataFrame 로드 성공.")
        return df
    except Exception as e:
        logging.error(f"'{filepath}' 파일 로드 중 오류 발생: {e}", exc_info=True)
        print(f"\n파일 로드 실패: {e}")
        return None

# 모듈 테스트를 위한 예시 (필요시 주석 해제 후 사용)
# if __name__ == "__main__":
#     print("--- scraping_utils 모듈 테스트 ---")
#
#     # 로깅 설정 테스트
#     setup_logging()
#
#     # 헤더 상수 테스트
#     print(f"기본 헤더: {DEFAULT_HEADERS}")
#
#     # URL 생성 함수 테스트
#     print(f"'backend' URL: {get_job_category_url('backend')}")
#     print(f"'frontend' URL: {get_job_category_url('frontend')}")
#     print(f"'total' URL: {get_job_category_url('total')}")
#     print(f"'unknown' URL (기본값): {get_job_category_url('unknown')}")
#
#     # Skill 필터링 함수 테스트
#     sample_skill = "Python\nJava\u2028JavaScript #Vue +Node.js 123 Test 456 Python"
#     filtered = filter_skill_data(sample_skill)
#     print(f"원본 Skill: '{sample_skill}'")
#     print(f"필터링된 Skill: '{filtered}'")
#     print(f"빈값 테스트: '{filter_skill_data('')}'")
#     print(f"None 테스트: '{filter_skill_data(None)}'")
#
#     # 데이터 저장 및 로드 함수 테스트
#     test_data = [
#         {'col1': 1, 'col2': 'A'},
#         {'col1': 2, 'col2': 'B'},
#         {'col1': 3, 'col2': 'C'}
#     ]
#     test_filename = 'test_output.csv'
#     test_folder = 'temp_data'
#
#     print(f"\n--- 데이터 저장 테스트 ---")
#     saved_filepath = save_data_to_csv(test_data, test_filename, folder=test_folder)
#
#     if saved_filepath:
#         print(f"\n--- 데이터 로드 테스트 ---")
#         loaded_df = load_data_from_csv(saved_filepath)
#         if loaded_df is not None:
#             print("로드된 데이터프레임:")
#             print(loaded_df)
#
#         # 존재하지 않는 파일 로드 테스트
#         print(f"\n--- 존재하지 않는 파일 로드 테스트 ---")
#         non_existent_df = load_data_from_csv('non_existent.csv')
#         print(f"non_existent_df: {non_existent_df}")
#
#         # 테스트 파일 및 폴더 정리 (선택 사항)
#         # import shutil
#         # if os.path.exists(test_folder):
#         #     shutil.rmtree(test_folder)
#         #     print(f"'{test_folder}' 폴더 삭제 완료.")