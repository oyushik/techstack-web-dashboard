import plotly.express as px
import plotly.graph_objects as go
import pandas as pd # 데이터프레임 처리를 위해 필요

def create_animated_bar_chart(data_df, x_col, y_col, title, orientation="v", color_scale="Plasma"):
    """
    주어진 데이터프레임을 사용하여 애니메이션 막대 그래프(Plotly)를 생성합니다.

    Args:
        data_df: 그래프를 그릴 데이터 (Pandas DataFrame, x_col, y_col 컬럼 포함).
        x_col: X축으로 사용할 컬럼 이름.
        y_col: Y축으로 사용할 컬럼 이름 (애니메이션될 빈도 값).
        title: 그래프 제목.
        orientation: 막대 방향 ('v' for vertical, 'h' for horizontal).
        color_scale: 막대에 사용할 색상 스케일 이름 (Plotly 내장).

    Returns:
        Plotly go.Figure 객체 또는 데이터가 비어있을 경우 None.
    """
    if data_df.empty:
        # 데이터가 비어있으면 None을 반환
        return None

    # 애니메이션 프레임 설정
    animation_frames = []
    # 0에서 100%까지 7단계로 나누어 프레임 생성 (총 8개 스텝: 0/7 ~ 7/7. 실제 애니메이션은 1/7부터 시작)
    # 초기 상태는 데이터의 0을 사용하므로 프레임은 1부터 7까지 생성합니다.
    for i in range(1, 8): # 1/7, 2/7, ..., 7/7 비율
        subset = data_df.copy()
        # 현재 프레임의 막대 높이(또는 길이) 계산: 최종 값 * (i / 7)
        # round(1)로 소수점 첫째 자리까지 반올림하여 데이터 크기 줄임
        subset["animated_count"] = (subset[y_col] * (i / 7)).round(1)

        # 각 프레임에 해당하는 Plotly Bar trace 데이터 생성
        if orientation == "h": # 가로 막대 그래프
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset["animated_count"], # 애니메이션될 값 (빈도)
                        y=subset[x_col], # 카테고리 (기술 스택, 기업 이름 등) - 변화 없음
                        orientation="h",
                        marker=dict(
                            color=subset["animated_count"], # 막대 색상도 빈도 값에 따라 변경
                            colorscale=color_scale,
                            showscale=True, # 컬러바 표시
                            colorbar=dict(title="빈도"), # 컬러바 제목
                        ),
                        text=subset["animated_count"].round(0).astype(int), # 막대 끝에 표시될 텍스트 (정수형으로 표시)
                        textposition="outside", # 막대 외부에 텍스트 표시
                        hovertemplate="<b>%{y}</b><br>빈도: %{x:,}", # 툴팁 형식
                    )
                ],
                name=f"frame{i}", # 프레임 고유 이름
            )
        else: # orientation == "v" (세로 막대 그래프)
            frame = go.Frame(
                data=[
                    go.Bar(
                        x=subset[x_col], # 카테고리 (변화 없음)
                        y=subset["animated_count"], # 애니메이션될 값 (빈도)
                        marker=dict(
                            color=subset["animated_count"], # 막대 색상도 빈도 값에 따라 변경
                            colorscale=color_scale,
                            showscale=True, # 컬러바 표시
                            colorbar=dict(title="빈도"), # 컬러바 제목
                        ),
                        text=subset["animated_count"].round(0).astype(int), # 막대 끝에 표시될 텍스트 (정수형으로 표시)
                        textposition="outside", # 막대 외부에 텍스트 표시
                        hovertemplate="<b>%{x}</b><br>빈도: %{y:,}", # 툴팁 형식
                    )
                ],
                name=f"frame{i}", # 프레임 고유 이름
            )
        animation_frames.append(frame)

    # 그래프 초기 상태 생성 (막대 높이/길이가 0인 상태)
    # 데이터프레임이 비어있을 경우 빈 리스트를 사용하여 오류 방지
    initial_values = [0] * len(data_df) if not data_df.empty else []

    if orientation == "h": # 가로 막대 그래프 초기 상태
        fig = go.Figure(
            data=[
                go.Bar(
                    x=initial_values, # 초기 x 값 (모두 0)
                    y=data_df[x_col] if not data_df.empty else [], # y 값 (카테고리)
                    orientation="h",
                    marker=dict(
                        color=initial_values, # 초기 색상 (0에 해당하는 색)
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=initial_values, # 초기 텍스트 (모두 0)
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>빈도: %{x:,}",
                )
            ],
            frames=animation_frames, # 정의된 애니메이션 프레임 연결
        )

        # x축 (빈도) 범위 설정: 최대값의 1.1배까지
        # 데이터가 비어있거나 최대값이 0인 경우 기본값 설정하여 오류 방지
        xmax = data_df[y_col].max() * 1.1 if not data_df.empty and data_df[y_col].max() > 0 else (1 if not data_df.empty else 1)
        fig.update_layout(
            xaxis_title="빈도",
            yaxis_title="",
            xaxis_range=[0, xmax], # X축 범위
            yaxis={"categoryorder": "total ascending"}, # Y축 (카테고리) 빈도 기준 오름차순 정렬
            bargap=0.15 # 막대 간 간격
        )
    else: # orientation == "v" (세로 막대 그래프 초기 상태)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=data_df[x_col] if not data_df.empty else [], # x 값 (카테고리)
                    y=initial_values, # 초기 y 값 (모두 0)
                    marker=dict(
                        color=initial_values, # 초기 색상 (0에 해당하는 색)
                        colorscale=color_scale,
                        showscale=True,
                        colorbar=dict(title="빈도"),
                    ),
                    text=initial_values, # 초기 텍스트 (모두 0)
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>빈도: %{y:,}",
                )
            ],
            frames=animation_frames, # 정의된 애니메이션 프레임 연결
        )

        # y축 (빈도) 범위 설정: 최대값의 1.1배까지
        # 데이터가 비어있거나 최대값이 0인 경우 기본값 설정하여 오류 방지
        ymax = data_df[y_col].max() * 1.1 if not data_df.empty and data_df[y_col].max() > 0 else (1 if not data_df.empty else 1)
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
        # updatemenus 블록은 자동 재생을 위해 제거 (재생 버튼 없음)
        # animation_duration=1000, # 선택 사항: 전체 애니메이션 시간 (트리거 필요)
        # transition={'duration': 500, 'easing': 'cubic-in-out'} # 선택 사항: 전환 부드럽게 (트리거 필요)
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "▶️ 그래프 표시",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 200, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 10},
                "showactive": False,
                "x": 0.5,
                "y": 1.15,
                "xanchor": "center",
                "yanchor": "top",
            }
        ],
    )

    return fig
