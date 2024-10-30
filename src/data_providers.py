"""
データ取得ロジックモジュール
"""
from logging import Logger
import pandas as pd
from .database import DatabricksConnection
from .config import DatabricksConfig

class DataProvider:
    def __init__(self, config: DatabricksConfig, logger: Logger):
        self.connection = DatabricksConnection(config, logger)
        self.logger = logger

class UpselltalkDataProvider(DataProvider):
    def get_data(self) -> pd.DataFrame:
        """
        フィードバックデータを取得し、適切なデータ型に変換
        """
        query = """
        SELECT *
        FROM common.mart.kotobal_wacoal_log
        """
        df = self.connection.execute_query(query)
        
        return df