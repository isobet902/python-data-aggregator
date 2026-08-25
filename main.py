
import logging
import os
import argparse
import matplotlib.pyplot as plt
import pandas as pd
 
import japanize_matplotlib  # これだけでOK、rcParamsの手動設定は削除
 
# ログの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 
 
def process_sales_data(input_file, output_csv, output_graph, start_date=None, end_date=None):
    try:
        logging.info("データの読み込みを開始します。")
 
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"{input_file} が見つかりません。")
 
        df = pd.read_csv(input_file)
 
        # --- ここから追加部分: 日付での絞り込み ---
        # 「日付」列を日付として扱えるように変換する
        df['日付'] = pd.to_datetime(df['日付'], errors='coerce')
 
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df['日付'] >= start_date]
            logging.info(f"開始日 {start_date.date()} 以降のデータに絞り込みました。")
 
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df['日付'] <= end_date]
            logging.info(f"終了日 {end_date.date()} 以前のデータに絞り込みました。")
 
        if df.empty:
            logging.error("指定した条件に一致するデータがありませんでした。")
            return
        # --- 追加部分ここまで ---
 
        # 売上金額の計算
        df['売上高'] = df['数量'] * df['単価']
 
        # カテゴリ別の合計売上を集計
        summary = df.groupby('カテゴリ')['売上高'].sum().reset_index()
        logging.info("集計が完了しました。")
 
        # 結果をCSV出力
        summary.to_csv(output_csv, index=False, encoding='utf-8-sig')
        logging.info(f"集計結果を {output_csv} に保存しました。")
 
        # グラフ化して画像出力
        plt.figure(figsize=(6, 4))
        plt.bar(summary['カテゴリ'], summary['売上高'])
        plt.title('カテゴリ別売上高')
        plt.xlabel('カテゴリ')
        plt.ylabel('売上高')
        plt.tight_layout()
        plt.savefig(output_graph)
        plt.close()  # メモリ解放
        logging.info(f"グラフを {output_graph} に保存しました。")
 
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
 
 
# --- ここから追加部分: コマンドライン引数の設定 ---
def build_arg_parser():
    parser = argparse.ArgumentParser(description="売上CSVをカテゴリ別に集計してグラフ化するツール")
    parser.add_argument('--input', default='data.csv', help='入力CSVファイル名(デフォルト: data.csv)')
    parser.add_argument('--output_csv', default='summary.csv', help='出力する集計CSVファイル名(デフォルト: summary.csv)')
    parser.add_argument('--output_graph', default='chart.png', help='出力するグラフ画像ファイル名(デフォルト: chart.png)')
    parser.add_argument('--start', default=None, help='集計開始日(例: 2026-08-01)。省略時は全期間')
    parser.add_argument('--end', default=None, help='集計終了日(例: 2026-08-05)。省略時は全期間')
    return parser
# --- 追加部分ここまで ---
 
 
if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    process_sales_data(
        args.input,
        args.output_csv,
        args.output_graph,
        start_date=args.start,
        end_date=args.end,
    )