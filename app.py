import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="서울시 미세먼지 대시보드", page_icon="😷", layout="wide")
st.title("😷 서울시 구별 (초)미세먼지 시각화 대시보드")

# 2. 데이터 로드 및 전처리 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    # 파일명은 실제 업로드한 파일명과 동일해야 합니다.
    df = pd.read_csv("dustdata.csv")
    
    # '일시' 컬럼을 날짜시간 데이터로 변환
    df['일시'] = pd.to_datetime(df['일시'])
    
    # 결측치(데이터가 없는 부분)는 시각화를 위해 제거
    df = df.dropna(subset=['미세먼지(PM10)', '초미세먼지(PM25)'])
    
    return df

df = load_data()

# 3. 사이드바 설정 (검색 및 필터링 기능)
st.sidebar.header("🔍 검색 조건 설정")

# 자치구 다중 선택 기능
gu_list = sorted(df['구분'].unique().tolist())
# 기본값으로 '평균'과 '강남구'를 설정
default_gu = ['평균', '강남구'] if '평균' in gu_list else [gu_list[0]]
selected_gu = st.sidebar.multiselect("확인할 자치구를 선택하세요:", gu_list, default=default_gu)

# 조회할 날짜 범위 선택 기능
min_date = df['일시'].min().date()
max_date = df['일시'].max().date()

selected_date = st.sidebar.date_input(
    "조회할 기간을 선택하세요:",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# 4. 데이터 필터링 및 시각화
if len(selected_date) == 2:
    start_date, end_date = selected_date
    
    # 선택된 구와 날짜에 맞게 데이터 추리기
    filtered_df = df[
        (df['구분'].isin(selected_gu)) &
        (df['일시'].dt.date >= start_date) &
        (df['일시'].dt.date <= end_date)
    ]
    
    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    else:
        # 미세먼지(PM10) 그래프
        st.subheader("📊 미세먼지 (PM10) 시간별 추이")
        fig_pm10 = px.line(filtered_df, x='일시', y='미세먼지(PM10)', color='구분', 
                           markers=True, template="plotly_white")
        st.plotly_chart(fig_pm10, use_container_width=True)

        # 초미세먼지(PM25) 그래프
        st.subheader("📉 초미세먼지 (PM25) 시간별 추이")
        fig_pm25 = px.line(filtered_df, x='일시', y='초미세먼지(PM25)', color='구분', 
                           markers=True, template="plotly_white")
        st.plotly_chart(fig_pm25, use_container_width=True)
        
        # 원본 데이터 확인 탭
        with st.expander("원본 데이터 테이블 보기"):
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
else:
    st.info("👆 사이드바에서 시작일과 종료일을 모두 선택해주세요.")
