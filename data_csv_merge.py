import os
import pandas as pd

def merge_csv_files(directory='./data'):
    """
    지정된 디렉토리 내의 CSV 파일들을 특정 규칙에 따라 통합하여 저장합니다.

    Args:
        directory (str, optional): CSV 파일들이 위치한 디렉토리 경로. 기본값은 './data'입니다.
    """

    all_files = os.listdir(directory)
    backend_files = [f for f in all_files if f.endswith('_backend.csv')]
    frontend_files = [f for f in all_files if f.endswith('_frontend.csv')]
    total_files = [f for f in all_files if f.endswith('_total.csv')]

    merged_backend_df = pd.DataFrame()
    if backend_files:
        backend_dfs = [pd.read_csv(os.path.join(directory, f)) for f in backend_files]
        merged_backend_df = pd.concat(backend_dfs, ignore_index=True)
        merged_backend_df.to_csv(os.path.join(directory, 'merged_data_backend.csv'), index=False)
        print("merged_data_backend.csv 파일이 성공적으로 저장되었습니다.")

    merged_frontend_df = pd.DataFrame()
    if frontend_files:
        frontend_dfs = [pd.read_csv(os.path.join(directory, f)) for f in frontend_files]
        merged_frontend_df = pd.concat(frontend_dfs, ignore_index=True)
        merged_frontend_df.to_csv(os.path.join(directory, 'merged_data_frontend.csv'), index=False)
        print("merged_data_frontend.csv 파일이 성공적으로 저장되었습니다.")

    merged_total_df = pd.DataFrame()
    if total_files:
        total_dfs = [pd.read_csv(os.path.join(directory, f)) for f in total_files]
        merged_total_df = pd.concat(total_dfs, ignore_index=True)
        merged_total_df.to_csv(os.path.join(directory, 'merged_data_total.csv'), index=False)
        print("merged_data_total.csv 파일이 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    merge_csv_files()