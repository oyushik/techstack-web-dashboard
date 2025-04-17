import os
import pandas as pd

def merge_and_deduplicate_csv_files(directory='./data', deduplication_columns=None):
    """
    지정된 디렉토리 내의 CSV 파일들을 특정 규칙에 따라 통합하고, 지정된 컬럼 기준으로 중복을 제거하여 저장합니다.

    Args:
        directory (str, optional): CSV 파일들이 위치한 디렉토리 경로. 기본값은 './data'입니다.
        deduplication_columns (list, optional): 중복 제거를 위한 컬럼 이름 리스트. 기본값은 None입니다.
    """

    if deduplication_columns is None or len(deduplication_columns) != 2:
        print("중복 제거를 위해서는 두 개의 컬럼 이름이 필요합니다.")
        return

    all_files = os.listdir(directory)
    backend_files = [f for f in all_files if f.endswith('_backend.csv')]
    frontend_files = [f for f in all_files if f.endswith('_frontend.csv')]
    total_files = [f for f in all_files if f.endswith('_total.csv')]

    def process_and_save(files, output_filename):
        if files:
            dfs = [pd.read_csv(os.path.join(directory, f)) for f in files]
            merged_df = pd.concat(dfs, ignore_index=True)
            # 중복 제거
            merged_df.drop_duplicates(subset=deduplication_columns, keep='first', inplace=True)
            merged_df.to_csv(os.path.join(directory, output_filename), index=False)
            print(f"{output_filename} 파일이 성공적으로 저장되었습니다 (중복 제거됨).")
        else:
            print(f"{output_filename} 에 해당하는 파일이 없습니다.")

    process_and_save(backend_files, 'data_merged_backend.csv')
    process_and_save(frontend_files, 'data_merged_frontend.csv')
    process_and_save(total_files, 'data_merged_total.csv')

if __name__ == "__main__":
    # 중복 제거를 원하는 컬럼 이름을 리스트 형태로 전달하세요.
    deduplication_columns = ["company", "skill"]
    merge_and_deduplicate_csv_files(deduplication_columns=deduplication_columns)