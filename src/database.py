"""
データベース接続管理モジュール
"""
from logging import Logger
import pandas as pd
from databricks import sql
from contextlib import contextmanager
from .config import DatabricksConfig

class DatabricksConnection:
    def __init__(self, config: DatabricksConfig, logger: Logger):
        self.config = config
        self.logger = logger

    @contextmanager
    def get_connection(self):
        """
        コンテキストマネージャとしてデータベース接続を提供
        """
        connection = None
        try:
            connection = sql.connect(
                server_hostname=self.config.server_hostname,
                http_path=self.config.http_path,
                access_token=self.config.access_token
            )
            yield connection
        except Exception as e:
            self.logger.error(f"データベース接続エラー: {str(e)}")
            raise
        finally:
            if connection:
                connection.close()

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        SQLクエリを実行してDataFrameとして結果を返す
        """
        self.logger.debug(f"クエリを実行: {query}")
        
        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
        return pd.DataFrame(result, columns=columns)