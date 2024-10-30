"""
設定管理モジュール
"""
import os
from dataclasses import dataclass
import streamlit as st
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class DatabricksConfig:
    server_hostname: str
    access_token: str
    http_path: str

def load_environment_variables() -> Dict[str, str]:
    """
    環境設定を読み込む
    優先順位:
    1. Streamlit Secrets (本番環境)
    2. 環境変数
    3. .envファイル (開発環境)
    """
    # Streamlit Cloud環境の確認
    try:
        if st.runtime.exists():
            logger.info("Streamlit Cloud環境で実行中")
            return {
                "server_hostname": st.secrets["databricks"]["server_hostname"],
                "access_token": st.secrets["databricks"]["access_token"],
                "http_path": st.secrets["databricks"]["http_path"]
            }
    except Exception as e:
        logger.warning(f"Streamlit Secretsの読み込みに失敗: {str(e)}")

    # ローカル開発環境
    logger.info("ローカル環境で実行中")
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenvがインストールされていません。環境変数のみを使用します。")

    # 環境変数からの読み込み
    config = {}
    env_vars = {
        "DATABRICKS_SERVER_HOSTNAME": "server_hostname",
        "DATABRICKS_TOKEN": "access_token",
        "DATABRICKS_HTTP_PATH": "http_path"
    }

    missing_vars = []
    for env_var, config_key in env_vars.items():
        value = os.getenv(env_var)
        if value is None:
            missing_vars.append(env_var)
        else:
            config[config_key] = value

    if missing_vars:
        raise ValueError(
            f"必要な環境変数が設定されていません: {', '.join(missing_vars)}\n"
            f".envファイルを作成するか、環境変数を設定してください。"
        )

    return config

def load_config() -> DatabricksConfig:
    """
    設定を読み込んでDatabricksConfigオブジェクトを返す
    """
    try:
        config_dict = load_environment_variables()
        return DatabricksConfig(**config_dict)
    except Exception as e:
        logger.error(f"設定の読み込みに失敗しました: {str(e)}")
        raise

    