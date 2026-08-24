import os
import pandas as pd
from main import process_sales_data

def test_process_sales_data():
    # テスト実行
    process_sales_data('data.csv', 'test_summary.csv', 'test_chart.png')

    # ファイルが生成されたか確認
    assert os.path.exists('test_summary.csv')
    assert os.path.exists('test_chart.png')

    # 後片付け
    if os.path.exists('test_summary.csv'):
        os.remove('test_summary.csv')
    if os.path.exists('test_chart.png'):
        os.remove('test_chart.png')