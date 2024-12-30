"""
GeminiLLMクラスのテスト
"""
import asyncio
from unittest.mock import Mock, patch

import pytest

from app.llm.gemini import GeminiLLM


@pytest.fixture
def gemini_config():
    """Gemini LLMの設定"""
    return {
        "api_key": "test_api_key",
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.1,
    }


@pytest.fixture
def mock_client():
    """モックされたGeminiクライアント"""
    with patch("google.generativeai.configure"), patch(
        "google.generativeai.GenerativeModel"
    ) as mock_model:
        mock_instance = Mock()
        mock_model.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def gemini_llm(gemini_config, mock_client):
    """GeminiLLMインスタンス"""
    llm = GeminiLLM(**gemini_config)
    llm.client = mock_client
    return llm


def test_init_client_success(gemini_config):
    """クライアント初期化の成功テスト"""
    llm = GeminiLLM(**gemini_config)
    assert llm.client is not None


def test_init_client_no_api_key():
    """API keyなしでの初期化テスト"""
    with pytest.raises(ValueError) as exc_info:
        GeminiLLM(api_key=None)
    assert "APIキーが設定されていません" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_success(gemini_llm):
    """テキスト生成の成功テスト"""
    mock_response = Mock()
    mock_response.text = "生成されたテキスト"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.generate_text("テストプロンプト")

    assert result == "生成されたテキスト"
    gemini_llm.client.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_success(gemini_llm):
    """コンテンツ分析の成功テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.analyze_content("テストコンテンツ", "test_task")

    assert result == {"key": "value"}
    gemini_llm.client.generate_content_async.assert_called_once()


@pytest.mark.asyncio
async def test_metrics_update(gemini_llm):
    """メトリクス更新のテスト"""
    mock_response = Mock()
    mock_response.text = "テストレスポンス"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    await gemini_llm.generate_text("テストプロンプト")

    # プロンプトとレスポンスの文字数でメトリクスが更新されていることを確認
    assert gemini_llm.metrics.prompt_tokens > 0
    assert gemini_llm.metrics.completion_tokens > 0
    assert gemini_llm.metrics.total_cost == 0.0  # 現在は無料


@pytest.mark.asyncio
async def test_json_extraction(gemini_llm):
    """JSONコンテンツ抽出のテスト"""
    test_cases = [
        # 正常なJSONケース
        {"input": '{"key": "value"}', "expected": {"key": "value"}},
        # JSONが文章の中に埋め込まれているケース
        {
            "input": '分析結果は以下の通りです：\n{"key": "value"}\n以上です。',
            "expected": {"key": "value"},
        },
        # 不正なJSONケース
        {"input": "これはJSONではありません", "expected": {"text": "これはJSONではありません"}},
    ]

    for case in test_cases:
        result = gemini_llm._extract_content(case["input"])
        assert result == case["expected"]


@pytest.mark.asyncio
async def test_retry_on_error(gemini_llm):
    """エラー時のリトライ機能のテスト"""
    # 2回失敗して3回目で成功するモックを作成
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        mock_response,
    ]

    result = await gemini_llm._analyze_content_impl("test", "test_task")

    # 3回呼び出されたことを確認
    assert gemini_llm.client.generate_content_async.call_count == 3
    # 最終的に成功したレスポンスが返されることを確認
    assert isinstance(result, dict)


@pytest.mark.parametrize(
    "task,content,expected_keywords",
    [
        (
            "selector",
            "<div>テストコンテンツ</div>",
            ["CSSセレクタ", "JSON", "title", "content", "date"],
        ),
        (
            "extract",
            "<div>テストコンテンツ</div>",
            ["HTML", "JSON", "title", "content", "date"],
        ),
        (
            "error",
            "テストエラー",
            ["エラー", "JSON", "cause", "solution", "retry"],
        ),
        (
            "url_analysis",
            "https://example.com/about/",
            ["URL", "JSON", "relevance_score", "category", "confidence"],
        ),
        (
            "unknown_task",
            "テストコンテンツ",
            ["分析", "内容"],
        ),
    ],
)
def test_create_analysis_prompt(gemini_llm, task, content, expected_keywords):
    """プロンプト生成機能のテスト"""
    prompt = gemini_llm._create_analysis_prompt(task, content)

    # プロンプトにコンテンツが含まれていることを確認
    assert content in prompt

    # 期待されるキーワードが含まれていることを確認
    for keyword in expected_keywords:
        assert keyword in prompt

    # プロンプトが文字列型であることを確認
    assert isinstance(prompt, str)
    assert len(prompt) > 0


@pytest.mark.asyncio
async def test_generate_text_api_error(gemini_llm):
    """APIエラー発生時のテスト"""
    gemini_llm.client.generate_content_async.side_effect = Exception("API Error")

    with pytest.raises(Exception) as exc_info:
        await gemini_llm.generate_text("テストプロンプト")
    assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_text_empty_response(gemini_llm):
    """空レスポンス受信時のテスト"""
    mock_response = Mock()
    mock_response.text = ""

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.generate_text("テストプロンプト")
    assert result == ""
    assert gemini_llm.metrics.completion_tokens == 0


@pytest.mark.asyncio
async def test_generate_text_none_response(gemini_llm):
    """Noneレスポンス受信時のテスト"""
    future = asyncio.Future()
    future.set_result(None)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.generate_text("テストプロンプト")
    assert result == ""
    assert gemini_llm.metrics.completion_tokens == 0
    assert gemini_llm.metrics.error_count == 0


@pytest.mark.asyncio
async def test_analyze_content_empty_input(gemini_llm):
    """空のコンテンツ入力時のテスト"""
    result = await gemini_llm.analyze_content("", "test_task")
    assert result["relevance_score"] == 0.1
    assert result["category"] == "other"
    assert "空のコンテンツ" in result["reason"]
    assert result["confidence"] == 0.1


@pytest.mark.asyncio
async def test_analyze_content_invalid_task(gemini_llm):
    """無効なタスク指定時のテスト"""
    mock_response = Mock()
    mock_response.text = "無効なタスク"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.analyze_content("テストコンテンツ", "invalid_task")
    assert isinstance(result, dict)
    assert "text" in result


@pytest.mark.asyncio
async def test_analyze_content_invalid_json(gemini_llm):
    """不正なJSON形式のレスポンス処理テスト"""
    mock_response = Mock()
    mock_response.text = "これは有効なJSONではありません{invalid:json}"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.analyze_content("テストコンテンツ", "test_task")
    assert isinstance(result, dict)
    assert "text" in result
    assert result["text"] == "これは有効なJSONではありません{invalid:json}"


@pytest.mark.asyncio
async def test_retry_empty_response(gemini_llm):
    """空レスポンス時のリトライ動作テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    empty_response = Mock()
    empty_response.text = ""

    future_empty = asyncio.Future()
    future_empty.set_result(empty_response)
    future_success = asyncio.Future()
    future_success.set_result(mock_response)

    gemini_llm.client.generate_content_async.side_effect = [
        future_empty,
        future_empty,
        future_success,
    ]

    result = await gemini_llm._analyze_content_impl("test", "test_task")
    assert gemini_llm.client.generate_content_async.call_count == 3
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_retry_backoff_timing(gemini_llm):
    """指数バックオフの待機時間検証テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    future = asyncio.Future()
    future.set_result(mock_response)

    # エラーを2回発生させ、3回目で成功
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        future,
    ]

    start_time = asyncio.get_event_loop().time()
    await gemini_llm._analyze_content_impl("test", "test_task")
    end_time = asyncio.get_event_loop().time()

    # 最小待機時間の検証（1秒 + 2秒の待機）
    assert end_time - start_time >= 3.0


@pytest.mark.asyncio
async def test_retry_max_retries_reached(gemini_llm):
    """最大リトライ回数到達時の処理テスト"""
    # すべての試行でエラーを発生
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("Error 1"),
        Exception("Error 2"),
        Exception("Error 3"),
    ]

    result = await gemini_llm._analyze_content_impl("test", "test_task")
    assert gemini_llm.client.generate_content_async.call_count == 3
    assert result["category"] == "other"
    assert "分析エラー" in result["reason"]
    assert result["confidence"] == 0.1


@pytest.mark.asyncio
async def test_retry_metrics_update(gemini_llm):
    """リトライ間のメトリクス更新確認テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    future = asyncio.Future()
    future.set_result(mock_response)

    # 2回失敗して3回目で成功
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        future,
    ]

    initial_prompt_tokens = gemini_llm.metrics.prompt_tokens
    initial_completion_tokens = gemini_llm.metrics.completion_tokens

    await gemini_llm._analyze_content_impl("test", "test_task")

    # メトリクスが1回だけ更新されていることを確認（成功時のみ）
    assert gemini_llm.metrics.prompt_tokens > initial_prompt_tokens
    assert gemini_llm.metrics.completion_tokens > initial_completion_tokens


@pytest.mark.asyncio
async def test_metrics_accumulation(gemini_llm):
    """複数回呼び出し時の累積値確認テスト"""
    mock_response = Mock()
    mock_response.text = "テストレスポンス"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    initial_prompt_tokens = gemini_llm.metrics.prompt_tokens
    initial_completion_tokens = gemini_llm.metrics.completion_tokens

    # 複数回呼び出し
    for _ in range(3):
        await gemini_llm.generate_text("テストプロンプト")

    # メトリクスが累積されていることを確認
    assert gemini_llm.metrics.prompt_tokens == initial_prompt_tokens + len("テストプロンプト") * 3
    assert gemini_llm.metrics.completion_tokens == initial_completion_tokens + len("テストレスポンス") * 3


def test_metrics_reset(gemini_llm):
    """メトリクスリセット機能の動作確認テスト"""
    # メトリクスを更新
    gemini_llm.update_metrics(100, 200, 0.0)
    assert gemini_llm.metrics.prompt_tokens == 100
    assert gemini_llm.metrics.completion_tokens == 200

    # メトリクスをリセット
    gemini_llm.metrics.reset()
    assert gemini_llm.metrics.prompt_tokens == 0
    assert gemini_llm.metrics.completion_tokens == 0
    assert gemini_llm.metrics.total_cost == 0.0


@pytest.mark.asyncio
async def test_metrics_error_update(gemini_llm):
    """エラー時のメトリクス更新確認テスト"""
    # エラーを発生させる
    gemini_llm.client.generate_content_async.side_effect = Exception("Test Error")

    initial_error_count = gemini_llm.metrics.error_count
    test_prompt = "テストプロンプト"
    expected_prompt_tokens = len(test_prompt)

    try:
        await gemini_llm.generate_text(test_prompt)
    except Exception:
        pass

    # エラー時のメトリクス更新を確認
    assert gemini_llm.metrics.prompt_tokens == expected_prompt_tokens
    assert gemini_llm.metrics.completion_tokens == 0
    assert gemini_llm.metrics.error_count == initial_error_count + 1


@pytest.mark.asyncio
async def test_analyze_content_invalid_json_response(gemini_llm):
    """不正なJSON形式のレスポンス処理テスト"""
    mock_response = Mock()
    mock_response.text = "これは不正なJSONです"

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.return_value = future

    result = await gemini_llm.analyze_content("テストコンテンツ", "test_task")
    assert isinstance(result, dict)
    assert "text" in result
    assert result["text"] == "これは不正なJSONです"


@pytest.mark.asyncio
async def test_retry_exponential_backoff(gemini_llm):
    """指数バックオフの待機時間検証テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "value"}'

    # 3回のリトライで成功するケース
    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("First failure"),
        Exception("Second failure"),
        future,
    ]

    start_time = asyncio.get_event_loop().time()
    result = await gemini_llm._analyze_content_impl("test", "test_task")
    end_time = asyncio.get_event_loop().time()

    # 最小待機時間の検証（1秒 + 2秒）
    assert end_time - start_time >= 3.0
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_metrics_reset_after_error(gemini_llm):
    """エラー発生時のメトリクスリセットテスト"""
    # 初期状態を記録
    initial_prompt_tokens = gemini_llm.metrics.prompt_tokens
    initial_completion_tokens = gemini_llm.metrics.completion_tokens
    initial_total_cost = gemini_llm.metrics.total_cost

    # エラーを発生させる
    gemini_llm.client.generate_content_async.side_effect = Exception("API Error")

    try:
        await gemini_llm.generate_text("テストプロンプト")
    except Exception:
        pass

    # メトリクスが適切に更新されていることを確認
    assert gemini_llm.metrics.prompt_tokens > initial_prompt_tokens
    assert gemini_llm.metrics.completion_tokens == initial_completion_tokens
    assert gemini_llm.metrics.total_cost == initial_total_cost
    assert gemini_llm.metrics.error_count > 0


@pytest.mark.asyncio
async def test_analyze_content_with_retry_success(gemini_llm):
    """リトライ後に成功するコンテンツ分析テスト"""
    mock_response = Mock()
    mock_response.text = '{"key": "success"}'

    future = asyncio.Future()
    future.set_result(mock_response)
    gemini_llm.client.generate_content_async.side_effect = [
        Exception("Temporary failure"),
        future,
    ]

    result = await gemini_llm.analyze_content("テストコンテンツ", "test_task")
    
    assert result == {"key": "success"}
    assert gemini_llm.client.generate_content_async.call_count == 2
    assert gemini_llm.metrics.error_count == 1
