import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 売上データ集計 & グラフ化ツール")

# 1. ファイルアップロード機能
uploaded_file = st.file_uploader("CSVファイルをアップロードしてください", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # 日付列が存在する場合の処理
    if '日付' in df.columns:
        df['日付'] = pd.to_datetime(df['日付'])
        
        min_date = df['日付'].min().date()
        max_date = df['日付'].max().date()
        
        st.sidebar.header("フィルタ設定")
        start_date = st.sidebar.date_input("開始日", min_date)
        end_date = st.sidebar.date_input("終了日", max_date)
        
        # データの絞り込み
        mask = (df['日付'].dt.date >= start_date) & (df['日付'].dt.date <= end_date)
        df = df.loc[mask]

    if not df.empty:
        # 集計処理
        df['売上高'] = df['数量'] * df['単価']
        summary = df.groupby('カテゴリ')['売上高'].sum().reset_index()

        # データ表示
        st.subheader("集計結果")
        st.write(summary.to_html(index=False), unsafe_allow_html=True)

        # グラフ描画（Plotlyを使って文字化け・枠切れを完全回避）
        st.subheader("カテゴリ別売上高")
        fig = px.bar(
            summary, 
            x='カテゴリ', 
            y='売上高', 
            title="カテゴリ別売上高",
            text_auto=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("指定された期間内にデータが存在しません。")