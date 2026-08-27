import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 売上データ集計＆グラフ化ツール")
st.caption("CSVまたはExcelファイルをアップロードし、カテゴリ別の売上を集計・グラフ化します。列名が違っていても、あとで対応を選べます。")

# --- 0. 使い方の説明(図解) ---
with st.expander("📋 使い方(どんなファイルが必要?)", expanded=True):
    st.markdown(
        "このツールは、**「1つの商品が、どのカテゴリに属していて、いくつ・いくらで売れたか」**"
        "がわかるデータから、カテゴリ別の売上高を自動で計算してグラフ化します。"
    )

    # 図解(SVG):商品 → 属性(カテゴリ・数量・単価) → 売上高の計算、という流れを示す
    diagram_svg = """
    <svg width="100%" height="150" viewBox="0 0 620 150" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/>
        </marker>
      </defs>

      <rect x="10" y="45" width="130" height="60" rx="8" fill="#eef2ff" stroke="#4f46e5"/>
      <text x="75" y="70" font-size="14" text-anchor="middle" fill="#1e293b">商品名</text>
      <text x="75" y="90" font-size="12" text-anchor="middle" fill="#475569">(例: ルンバ)</text>

      <line x1="140" y1="75" x2="190" y2="75" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

      <rect x="200" y="10" width="150" height="35" rx="8" fill="#ecfdf5" stroke="#059669"/>
      <text x="275" y="33" font-size="13" text-anchor="middle" fill="#065f46">カテゴリ: 家電</text>

      <rect x="200" y="57" width="150" height="35" rx="8" fill="#ecfdf5" stroke="#059669"/>
      <text x="275" y="80" font-size="13" text-anchor="middle" fill="#065f46">数量: 1</text>

      <rect x="200" y="104" width="150" height="35" rx="8" fill="#ecfdf5" stroke="#059669"/>
      <text x="275" y="127" font-size="13" text-anchor="middle" fill="#065f46">単価: 50,000円</text>

      <line x1="350" y1="75" x2="400" y2="75" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrow)"/>

      <rect x="410" y="45" width="200" height="60" rx="8" fill="#fef3c7" stroke="#d97706"/>
      <text x="510" y="68" font-size="13" text-anchor="middle" fill="#92400e">売上高 = 単価 × 数量</text>
      <text x="510" y="88" font-size="12" text-anchor="middle" fill="#92400e">→ カテゴリ別に合計</text>
    </svg>
    """
    st.markdown(diagram_svg, unsafe_allow_html=True)

    st.markdown("**こんな形式のファイルが読み込めます(列名は多少違っていても、あとで対応を選べます)**")
    example_df = pd.DataFrame({
        "日付": ["2026-08-01", "2026-08-01", "2026-08-02"],
        "商品名": ["ルンバ", "マウス", "デスク"],
        "カテゴリ": ["家電", "家電", "家具"],
        "数量": [1, 5, 1],
        "単価": [50000, 3000, 25000],
    })
    st.dataframe(example_df, hide_index=True)
    st.caption("つまり、1行が「1つの商品の記録」になっていて、「カテゴリ」「数量」「単価」の3つの情報が読み取れれば大丈夫です。日付は無くても集計できます。")


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