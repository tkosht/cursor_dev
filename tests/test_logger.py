"""CustomLoggerのテスト"""

import json
import logging
import shutil

import pytest

from app.logger import CustomLogger, JsonFormatter, LogLevel


@pytest.fixture
def temp_log_dir(tmp_path):
    """一時的なログディレクトリを作成"""
    log_dir = tmp_path / "logs"
    yield log_dir
    # テスト後にログディレクトリを削除
    if log_dir.exists():
        shutil.rmtree(log_dir)


@pytest.fixture
def logger(temp_log_dir):
    """テスト用のロガーインスタンスを作成"""
    return CustomLogger("test_logger", str(temp_log_dir))


def test_logger_initialization(temp_log_dir):
    """ロガーの初期化テスト"""
    logger = CustomLogger("test_init", str(temp_log_dir))
    
    # ログディレクトリの作成を確認
    for level in ["debug", "info", "error"]:
        assert (temp_log_dir / level).exists()
        assert (temp_log_dir / level).is_dir()

    # ロガーの設定を確認
    assert logger.logger.name == "test_init"
    assert logger.logger.level == logging.DEBUG
    assert len(logger.logger.handlers) == 4  # 3つのファイルハンドラ + 1つのコンソールハンドラ


def test_log_file_creation(logger, temp_log_dir):
    """ログファイルの作成テスト"""
    logger.debug("デバッグメッセージ")
    logger.info("情報メッセージ")
    logger.warning("警告メッセージ")
    logger.error("エラーメッセージ")

    # 各レベルのログファイルが作成されていることを確認
    assert (temp_log_dir / "debug" / "test_logger.log").exists()
    assert (temp_log_dir / "info" / "test_logger.log").exists()
    assert (temp_log_dir / "error" / "test_logger.log").exists()


def test_log_content(logger, temp_log_dir):
    """ログ内容のテスト"""
    test_message = "テストメッセージ"
    test_details = {"key": "value"}
    
    # 各レベルでログを出力
    logger.debug(test_message, test_details)
    logger.info(test_message, test_details)
    logger.warning(test_message, test_details)
    logger.error(test_message, test_details)

    # デバッグログの内容を確認
    debug_log_path = temp_log_dir / "debug" / "test_logger.log"
    with open(debug_log_path, "r", encoding="utf-8") as f:
        log_entry = json.loads(f.readline())
        assert log_entry["level"] == "DEBUG"
        assert log_entry["message"] == test_message
        assert log_entry["details"] == test_details
        assert "timestamp" in log_entry
        assert "module" in log_entry
        assert "function" in log_entry


def test_log_rotation(temp_log_dir):
    """ログローテーションのテスト"""
    # 小さいサイズでログローテーションを設定
    logger = CustomLogger(
        "test_rotation",
        str(temp_log_dir),
        max_bytes=100,
        backup_count=2
    )

    # ログローテーションが発生するまでログを出力
    for i in range(100):
        logger.debug(f"テストメッセージ {i}")

    debug_dir = temp_log_dir / "debug"
    log_files = list(debug_dir.glob("test_rotation.log*"))
    
    # メインのログファイルと2つのバックアップファイルが存在することを確認
    assert len(log_files) == 3
    assert (debug_dir / "test_rotation.log").exists()
    assert (debug_dir / "test_rotation.log.1").exists()
    assert (debug_dir / "test_rotation.log.2").exists()


def test_log_levels(logger):
    """ログレベルのテスト"""
    assert LogLevel.DEBUG == 10
    assert LogLevel.INFO == 20
    assert LogLevel.WARNING == 30
    assert LogLevel.ERROR == 40 


def test_json_formatter():
    """JSONフォーマッタのテスト"""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="テストメッセージ",
        args=(),
        exc_info=None
    )

    # 基本的なフォーマット
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    assert log_data["level"] == "INFO"
    assert log_data["message"] == "テストメッセージ"
    assert log_data["module"] == "test"
    assert isinstance(log_data["timestamp"], str)

    # 特殊文字を含むメッセージ
    record.msg = "特殊文字: \n\t\r"
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    assert log_data["message"] == "特殊文字: \n\t\r"

    # 複雑なdetails辞書
    complex_details = {
        "nested": {"key": "value"},
        "list": [1, 2, 3],
        "unicode": "日本語",
        "special": "\n\t\r"
    }
    record.msg = "詳細付きメッセージ"
    setattr(record, "details", complex_details)
    formatted = formatter.format(record)
    log_data = json.loads(formatted)
    assert log_data["details"] == complex_details 


def test_log_level_filtering(logger, temp_log_dir):
    """ログレベルフィルタリングのテスト"""
    # DEBUGメッセージを出力
    debug_msg = "デバッグメッセージ"
    logger.debug(debug_msg)

    # INFOメッセージを出力
    info_msg = "情報メッセージ"
    logger.info(info_msg)

    # WARNINGメッセージを出力
    warning_msg = "警告メッセージ"
    logger.warning(warning_msg)

    # ERRORメッセージを出力
    error_msg = "エラーメッセージ"
    logger.error(error_msg)

    # INFOログファイルを確認（DEBUGメッセージが含まれていないことを確認）
    info_log_path = temp_log_dir / "info" / "test_logger.log"
    with open(info_log_path, "r", encoding="utf-8") as f:
        info_logs = f.readlines()
        info_messages = [json.loads(log)["message"] for log in info_logs]
        assert debug_msg not in info_messages
        assert info_msg in info_messages
        assert warning_msg in info_messages
        assert error_msg in info_messages

    # ERRORログファイルを確認（WARNING以下のメッセージが含まれていないことを確認）
    error_log_path = temp_log_dir / "error" / "test_logger.log"
    with open(error_log_path, "r", encoding="utf-8") as f:
        error_logs = f.readlines()
        error_messages = [json.loads(log)["message"] for log in error_logs]
        assert debug_msg not in error_messages
        assert info_msg not in error_messages
        assert warning_msg not in error_messages
        assert error_msg in error_messages 