import logging
import os
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import japanize_matplotlib  # ← これを追加
import pandas as pd

# Windows用：日本語フォントの設定（豆腐化対策）
plt.rcParams['font.family'] = 'MS Gothic'

# ログの設定（実行状況を記録する）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_sales_data(input_file, output_csv, output_graph):
    try:
        logging.info("データの読み込みを開始します。")
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"{input_file} が見つかりません。")

        df = pd.read_csv(input_file)

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
        plt.title('Sales by Category')
        plt.xlabel('Category')
        plt.ylabel('Sales')
        plt.tight_layout()
        plt.savefig(output_graph)
        logging.info(f"グラフを {output_graph} に保存しました。")

    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    process_sales_data('data.csv', 'summary.csv', 'chart.png')