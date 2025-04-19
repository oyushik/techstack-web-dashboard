import streamlit as st
import pandas as pd
from collections import Counter

def autopct_func(pct):
    """파이 차트의 퍼센트 표시 형식 함수 (현재 코드에서는 사용되지 않지만, 모듈에 포함)"""
    return f"{pct:.1f}%"

def count_skills(df):
    """
    주어진 데이터프레임의 'skill' 컬럼에서 기술 스택 빈도를 계산합니다.
    특정 제외 목록에 있는 스킬은 계산에서 제외합니다.
    """
    skill_counts = Counter()
    for index, row in df.iterrows():
        skills_str = row.get("skill") # .get()을 사용하여 컬럼이 없을 경우 오류 방지
        if pd.notna(skills_str) and isinstance(skills_str, str): # 문자열인지 확인
            # 쉼표로 분리하고 공백 제거 및 대문자 변환
            skills = [skill.strip().upper() for skill in skills_str.split(",")]
            skill_counts.update(skills)

    # count에서 제외될 스킬 목록 정의 (너무 일반적인 단어, 기술 스택이 아닌 것, 정규화 후 쓰레기값 등)
    # 이 목록은 data_loader 모듈 내부에 두거나 별도 설정 파일에서 관리할 수 있습니다.
    # 여기서는 임시로 함수 내부에 정의합니다.
    excluded_skills = ["AI", "UI", "UIUX", "NATIVE", "BOOT", "API", "WEB", "SW", "PC"]

    if excluded_skills:
        excluded_skills_upper = [skill.upper() for skill in excluded_skills]
        # 제외 목록에 없는 스킬만 결과에 포함
        skill_counts = {
            skill: count
            for skill, count in skill_counts.items()
            if skill not in excluded_skills_upper
        }

    # 결과를 Pandas Series로 변환하고 내림차순 정렬하여 반환
    return pd.Series(skill_counts).sort_values(ascending=False)

@st.cache_data(ttl=3600, show_spinner=False)
def load_csv_data(file_name):
    """
    CSV 파일을 읽어와 데이터프레임으로 로드합니다.
    Streamlit의 캐싱을 적용하여 데이터 로딩 성능을 최적화합니다.
    """
    try:
        # 'data' 서브폴더 내의 파일 경로 설정
        file_path = f"data/{file_name}"
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.warning(f"데이터 파일 '{file_name}'을(를) 찾을 수 없습니다. 'data' 폴더에 파일을 넣어주세요.")
        return None
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return None

def load_all_data():
    """
    애플리케이션에 필요한 모든 데이터 파일을 로드합니다.
    """
    data = {
        'total': load_csv_data("merged_data_total.csv"),
        'backend': load_csv_data("merged_data_backend.csv"),
        'frontend': load_csv_data("merged_data_frontend.csv")
    }
    return data

# autopct_func 함수는 현재 코드에서 직접 사용되지 않으므로 count_skills에 제외 리스트를 통합했습니다.
# 만약 autopct_func가 필요하다면 그대로 두거나 제거할 수 있습니다.
# 여기서는 count_skills 함수 내부에 excluded_skills를 넣는 방식으로 수정했습니다.
