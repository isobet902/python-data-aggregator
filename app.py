import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 売上データ集計＆グラフ化ツール")
st.caption("CSVまたはExcelファイルをアップロードし、カテゴリ別の売上を集計・グラフ化します。列名が違っていても、あとで対応を選べます。")

# --- 1. ファイルアップロード機能(CSV / Excel 両対応) ---
uploaded_file = st.file_uploader(
    "CSVまたはExcelファイルをアップロードしてください",
    type=["csv", "xlsx", "xls"],
)

if uploaded_file is not None:

    # 拡張子を見て、CSVかExcelかで読み込み方法を切り替える
    if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
        df_raw = pd.read_excel(uploaded_file)
    else:
        df_raw = pd.read_csv(uploaded_file)

    # --- 2. 列名マッピング機能 ---
    st.subheader("列の対応を選んでください")
    st.caption("アップロードしたファイルの列名が「日付・カテゴリ・数量・単価」と違っていても大丈夫です。どの列が何にあたるか選んでください。")

    columns = list(df_raw.columns)
    none_option = "(使用しない)"

    col1, col2 = st.columns(2)
    with col1:
        date_col = st.selectbox("「日付」に対応する列(任意)", [none_option] + columns)
        category_col = st.selectbox("「カテゴリ」に対応する列", columns)
    with col2:
        quantity_col = st.selectbox("「数量」に対応する列", columns)
        price_col = st.selectbox("「単価」に対応する列", columns)

    # 同じ列を重複して選んでいないかチェック
    selected = [category_col, quantity_col, price_col]
    if date_col != none_option:
        selected.append(date_col)

    if len(selected) != len(set(selected)):
        st.error("同じ列を複数の項目に割り当てています。それぞれ別の列を選んでください。")
        st.stop()

    # 選んだ列名を、プログラム内部で使う名前(日付・カテゴリ・数量・単価)に統一する
    rename_map = {
        category_col: "カテゴリ",
        quantity_col: "数量",
        price_col: "単価",
    }
    if date_col != none_option:
        rename_map[date_col] = "日付"

    df = df_raw.rename(columns=rename_map)

    # 数量・単価が数値として扱えるか変換(文字が混ざっていたらエラー値=NaNになる)
    df["数量"] = pd.to_numeric(df["数量"], errors="coerce")
    df["単価"] = pd.to_numeric(df["単価"], errors="coerce")

    if df["数量"].isna().any() or df["単価"].isna().any():
        st.warning("「数量」または「単価」に数値として読み取れない値が含まれていたため、該当行を除外しました。")
        df = df.dropna(subset=["数量", "単価"])

    # --- 3. 日付フィルタ機能(日付列を選んだ場合のみ表示) ---
    if date_col != none_option:
        df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
        df = df.dropna(subset=["日付"])

        if not df.empty:
            min_date = df["日付"].min().date()
            max_date = df["日付"].max().date()

            st.sidebar.header("フィルタ設定")
            start_date = st.sidebar.date_input("開始日", min_date, min_value=min_date, max_value=max_date)
            end_date = st.sidebar.date_input("終了日", max_date, min_value=min_date, max_value=max_date)

            mask = (df["日付"].dt.date >= start_date) & (df["日付"].dt.date <= end_date)
            df = df.loc[mask]

    # --- 4. 集計・表示 ---
    if not df.empty:
        df["売上高"] = df["数量"] * df["単価"]
        summary = df.groupby("カテゴリ")["売上高"].sum().reset_index()

        st.subheader("集計結果")
        st.write(summary.to_html(index=False), unsafe_allow_html=True)

        st.subheader("カテゴリ別売上高")
        fig = px.bar(
            summary,
            x="カテゴリ",
            y="売上高",
            title="カテゴリ別売上高",
            text_auto=True,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("指定された条件に一致するデータがありません。")

else:
    st.info("CSVまたはExcelファイルをアップロードしてください。")