import googleapiclient.discovery
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
# 이 함수는 스크립트의 시작 부분에서 한 번만 호출하면 됩니다.
load_dotenv()

def search_youtube(api_key, query, max_results=10):
    """
    YouTube Data API를 사용하여 동영상을 검색합니다.

    Args:
        api_key (str): 유효한 YouTube Data API 키.
        query (str): 검색할 키워드.
        max_results (int): 가져올 최대 검색 결과 개수.

    Returns:
        list: 검색 결과 동영상의 리스트 (제목, 설명, 동영상 ID 포함),
        또는 오류 발생 시 None.
    """
    try:
        # API 서비스 빌드
        # youtube 변수는 googleapiclient.discovery.build로 생성된 Resource 객체입니다.
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=api_key
        )

        # 검색 요청 실행:
        # youtube 객체의 search() 리소스에 접근하고, list() 메서드를 호출해야 합니다.
        # --- 수정된 부분 ---
        request = youtube.search().list(
        # ------------------
            part="snippet", # 결과에서 'snippet' 부분을 가져옴 (제목, 설명 등 포함)
            q=query,       # 검색 키워드
            type="video",  # 검색할 리소스 타입 (동영상)
            maxResults=max_results # 가져올 최대 결과 개수
        )
        response = request.execute()

        videos = []
        # 검색 결과 파싱
        for item in response.get("items", []):
            # 동영상 타입 결과만 처리
            if item["id"]["kind"] == "youtube#video":
                video_info = {
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "video_id": item["id"]["videoId"]
                }
                videos.append(video_info)

        return videos

    except googleapiclient.errors.HttpError as e:
        print(f"API 호출 중 오류 발생: {e}")
        # print(f"오류 상세 내용: {e.content}") # e.content는 바이너리 데이터일 수 있습니다. e 객체 자체에 유용한 정보가 포함될 가능성이 높습니다.
        return None
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return None

# --- 메인 실행 부분 ---
if __name__ == "__main__":
    # .env 파일에서 로드된 환경 변수를 가져옵니다.
    API_KEY = os.getenv("YOUR_YOUTUBE_API_KEY")

    # API 키가 제대로 로드되었는지 확인
    if not API_KEY:
        print("오류: 환경 변수 YOUR_YOUTUBE_API_KEY가 설정되지 않았거나 비어 있습니다.")
        print(".env 파일이 올바른 위치에 있는지, 변수 이름이 정확한지 확인하세요.")
        print("'pip install python-dotenv' 설치 및 'load_dotenv()' 호출을 확인하세요.")
    else:
        # 사용자로부터 검색 키워드 입력 받기
        # 여기서 아래 search_query 변수에 사용자 input 대신 키워드 넘겨 받으면 됨
        
        search_query = input("검색할 YouTube 동영상 키워드를 입력하세요: ")

        if search_query:
            print(f"'{search_query}'(으)로 YouTube 동영상을 검색합니다...")
            # Youtube 함수 호출 (api_key와 search_query 인자 전달)
            search_results = search_youtube(API_KEY, search_query)

            # 결과 출력
            # 이거를 web 화면에 띄우는 방식으로 수정해야 함
            if search_results is not None: # None이 아닌지 확인 (오류 발생 시 None 반환)
                if search_results: # 결과 리스트가 비어있지 않은지 확인
                    print("\n--- 검색 결과 ---")
                    for i, video in enumerate(search_results):
                        print(f"{i + 1}. 제목: {video['title']}")
                        # 설명은 최대 150자까지 출력하고 줄바꿈 문자를 공백으로 치환하여 보기 좋게
                        description = video['description'].replace('\n', ' ')
                        print(f"  설명: {description[:150]}...")
                        # --- 수정된 부분: 올바른 YouTube 링크 형식 사용 ---
                        print(f"  링크: https://www.youtube.com/watch?v={video['video_id']}")
                        # ----------------------------------------------
                        print("-" * 20)
                else:
                    print("검색 결과가 없습니다.")
            # else: Youtube 함수 내에서 오류 메시지가 이미 출력됨

        else:
            print("검색 키워드를 입력해주세요.")