"""
メインアプリケーション
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.config import load_config
from src.data_providers import UpselltalkDataProvider
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # タイトルの設定
        st.title("営業関連会話分析ダッシュボード")
        
        # 設定の読み込みとデータプロバイダーの初期化
        config = load_config()
        data_provider = UpselltalkDataProvider(config, logger)
        # データの取得
        df = data_provider.get_data()
        cols = ["ユーザ名","翻訳元言語", "翻訳先言語", "端末名" ,"日時", "翻訳原文", "翻訳文", "is_sales_related"]
        df = df[cols]
        
        # 日時カラムを datetime 型に変換
        df['日時'] = pd.to_datetime(df['日時'])
        
        # サイドバーにフィルター設定を配置
        st.sidebar.header('フィルター設定')
        
        # 営業関連フィルター
        sales_filter = st.sidebar.selectbox(
            'is_sales_related',
            ['すべて', True, False]
        )
        
        # 日付範囲フィルター
        min_date = df['日時'].min().date()
        max_date = df['日時'].max().date()
        date_range = st.sidebar.date_input(
            '日付範囲',
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # 端末名フィルター
        device_names = ['すべて'] + list(df['端末名'].unique())
        selected_device = st.sidebar.selectbox('端末名', device_names)
        
        # フィルター適用
        filtered_df = df.copy()
        
        # 営業関連フィルター適用
        if sales_filter != 'すべて':
            filtered_df = filtered_df[filtered_df['is_sales_related'] == sales_filter]
            
        # 日付フィルター適用
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['日時'].dt.date >= start_date) &
                (filtered_df['日時'].dt.date <= end_date)
            ]
            
        # 端末名フィルター適用
        if selected_device != 'すべて':
            filtered_df = filtered_df[filtered_df['端末名'] == selected_device]
        
        # 時系列グラフの作成
        st.header('営業関連会話の時系列推移')
        
        # 日ごとの集計データ作成
        daily_counts = filtered_df.groupby(filtered_df['日時'].dt.date)['is_sales_related'].sum().reset_index()
        daily_counts.columns = ['日付', '営業関連会話数']
        
        # グラフ描画
        fig = px.line(
            daily_counts,
            x='日付',
            y='営業関連会話数',
            title='日次営業関連会話数の推移'
        )
        st.plotly_chart(fig)
        
        # 基本統計情報の表示
        st.header('基本統計情報')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総会話数", len(filtered_df))
        with col2:
            st.metric("営業関連会話数", filtered_df['is_sales_related'].sum())
        with col3:
            sales_ratio = (filtered_df['is_sales_related'].sum() / len(filtered_df)) * 100
            st.metric("営業関連会話率", f"{sales_ratio:.1f}%")
        
        # データテーブルの表示
        st.header('詳細データ')
        st.dataframe(filtered_df)
        
    except Exception as e:
        logger.error(f"アプリケーションエラー: {str(e)}", exc_info=True)
        st.error(f"エラーが発生しました: {str(e)}")

if __name__ == '__main__':
    main()