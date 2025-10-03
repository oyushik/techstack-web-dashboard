import plotly.express as px
import plotly.graph_objects as go
import pandas as pd # 데이터프레임 처리를 위해 필요

def create_animated_bar_chart(data_df, x_col, y_col, title, orientation="v", color_scale="Plasma"):
    """
    주어진 데이터프레임을 사용하여 정적 막대 그래프(Plotly)를 생성합니다.

    Args:
        data_df: 그래프를 그릴 데이터 (Pandas DataFrame, x_col, y_col 컬럼 포함).
        x_col: X축으로 사용할 컬럼 이름.
        y_col: Y축으로 사용할 컬럼 이름 (빈도 값).
        title: 그래프 제목.
        orientation: 막대 방향 ('v' for vertical, 'h' for horizontal).
        color_scale: 막대에 사용할 색상 스케일 이름 (Plotly 내장).

    Returns:
        Plotly go.Figure 객체 또는 데이터가 비어있을 경우 None.
    """
    if data_df.empty:
        # 데이터가 비어있으면 None을 반환
        return None

    # 정적 그래프 생성 (애니메이션 제거)
    if orientation == "h": # 가로 막대 그래프
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_df[y_col], # 빈도 값
                    y=data_df[x_col], # 카테고리 (기술 스택, 기업 이름 등)
                    orientation="h",
                    marker=dict(
                        color=data_df[y_col], # 막대 색상
                        colorscale=color_scale,
                        showscale=True, # 컬러바 표시
                        colorbar=dict(title="빈도"), # 컬러바 제목
                    ),
                    text=data_df[y_col].round(0).astype(int), # 막대 끝에 표시될 텍스트
                    textposition="outside", # 막대 외부에 텍스트 표시
                    hovertemplate="<b>%{y}</b><br>빈도: %{x:,}", # 툴팁 형식
                )
            ]
        )

        # x축 (빈도) 범위 설정: 최대값의 1.1배까지
        xmax = data_df[y_col].max() * 1.1 if data_df[y_col].max() > 0 else 1
        fig.update_layout(
            xaxis_title="빈도",
            yaxis_title="",
            xaxis_range=[0, xmax], # X축 범위
            yaxis={"categoryorder": "total ascending"}, # Y축 (카테고리) 빈도 기준 오름차순 정렬
            bargap=0.15 # 막대 간 간격
        )
    else: # orientation == "v" (세로 막대 그래프)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_df[x_col], # 카테고리
                    y=data_df[y_col], # 빈도 값
                    marker=dict(
                        color=data_df[y_col], # 막대 색상
                        colorscale=color_scale,
                        showscale=True, # 컬러바 표시
                        colorbar=dict(title="빈도"), # 컬러바 제목
                    ),
                    text=data_df[y_col].round(0).astype(int), # 막대 끝에 표시될 텍스트
                    textposition="outside", # 막대 외부에 텍스트 표시
                    hovertemplate="<b>%{x}</b><br>빈도: %{y:,}", # 툴팁 형식
                )
            ]
        )

        # y축 (빈도) 범위 설정: 최대값의 1.1배까지
        ymax = data_df[y_col].max() * 1.1 if data_df[y_col].max() > 0 else 1
        fig.update_layout(
            xaxis_title="",
            yaxis_title="빈도",
            yaxis_range=[0, ymax], # Y축 범위
            xaxis=dict(tickangle=-45), # X축 (카테고리) 레이블 45도 회전
            bargap=0.15 # 막대 간 간격
        )

    # 공통 레이아웃 설정
    # 텍스트 레이블 잘림 방지 및 전체 레이아웃 조정
    # 마진 값은 텍스트 크기 및 레이블 길이에 따라 조정 필요
    adjusted_margin = dict(
        l=60 if orientation == "v" else 250, # 왼쪽 마진: 세로일 때 60, 가로일 때 텍스트 공간 확보 (예: 250)
        r=60, # 오른쪽 마진
        t=80 if orientation == "v" else 70, # 위쪽 마진: 세로일 때 텍스트 공간 확보 (예: 80), 가로 70 (제목)
        b=100 if orientation == "v" else 70 # 아래쪽 마진: 세로일 때 100 (x축 레이블), 가로 70
    )

    fig.update_layout(
        title={
            "text": title, # 그래프 제목
            "y": 0.95, "x": 0.5, # 제목 위치 (가운데 위)
            "xanchor": "center", "yanchor": "top",
        },
        height=600, # 그래프 높이 고정
        margin=adjusted_margin, # 조정된 마진 적용
    )

    return fig
