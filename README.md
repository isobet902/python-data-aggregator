# Python Sales Data Aggregator

CSV形式の売上データを自動で集計し、カテゴリ別の集計結果（CSV）と棒グラフ（PNG）を出力するデータ加工ツールです。

## 主な機能
- **自動集計**: CSVファイルを読み込み、カテゴリごとの売上合計を算出
- **可視化**: 集計結果を元に棒グラフ画像を自動生成
- **自動テスト**: `pytest` による動作検証ロジックを同梱

## 技術スタック
- Python 3.13
- pandas (データ加工)
- matplotlib (データ可視化)
- pytest (単体テスト)

## 実行方法
1. 依存ライブラリのインストール
   ```bash
   pip install pandas matplotlib pytest