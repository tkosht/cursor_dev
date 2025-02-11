"""LLMProcessorのテスト"""

import asyncio
import gc
from unittest.mock import AsyncMock, MagicMock, patch

import google.generativeai as genai
import ollama
import psutil
import pytest

from app.llm_processor import LLMProcessor, LLMProcessorError


@pytest.fixture
def processor():
    """テスト用のLLMProcessorインスタンス"""
    return LLMProcessor(model_type="gemini")


@pytest.fixture
def sample_context():
    """サンプルのコンテキストデータ"""
    return [
        {
            "id": "1",
            "url": "https://twitter.com/user/status/1",
            "text": "Pythonプログラミングが楽しい",
            "created_at": "1234567890",
        },
        {
            "id": "2",
            "url": "https://twitter.com/user/status/2",
            "text": "機械学習の最新論文を読んだ",
            "created_at": "1234567891",
        },
    ]


def test_init_with_invalid_model():
    """無効なモデルタイプでの初期化テスト"""
    with pytest.raises(LLMProcessorError) as exc_info:
        LLMProcessor(model_type="invalid_model")
    assert "サポートされていないモデルタイプです" in str(exc_info.value)


def test_format_context(processor, sample_context):
    """コンテキストのフォーマットテスト"""
    formatted = processor._format_context(sample_context)
    assert "Tweet: Pythonプログラミングが楽しい" in formatted
    assert "URL: https://twitter.com/user/status/1" in formatted
    assert "Tweet: 機械学習の最新論文を読んだ" in formatted
    assert "URL: https://twitter.com/user/status/2" in formatted


def test_create_prompt(processor, sample_context):
    """プロンプト生成テスト"""
    query = "Pythonについて教えて"
    prompt = processor._create_prompt(query, sample_context)
    assert "質問: Pythonについて教えて" in prompt
    assert "回答形式:" in prompt
    assert "1. 関連する情報を箇条書きで要約" in prompt


@pytest.mark.asyncio
async def test_generate_response_no_context(processor):
    """コンテキストが空の場合のレスポンス生成テスト"""
    response = await processor.generate_response("テストクエリ", [])
    assert "関連するブックマークが見つかりませんでした" in response


@pytest.mark.asyncio
async def test_generate_response_timeout(processor, sample_context):
    """タイムアウトのテスト"""
    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:

        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)
            return MagicMock(text="遅い応答")

        mock_generate.side_effect = slow_response
        with pytest.raises(LLMProcessorError) as exc_info:
            await processor.generate_response(
                "テストクエリ", sample_context, timeout=1
            )
        assert "タイムアウト" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_gemini_response(processor):
    """Geminiモデルのレスポンス生成テスト"""
    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.return_value = MagicMock(text="テスト回答")
        response = await processor._generate_gemini_response(
            "テストプロンプト"
        )
        assert response == "テスト回答"
        mock_generate.assert_called_once_with("テストプロンプト")


@pytest.mark.asyncio
async def test_generate_gpt_response():
    """GPTモデルのレスポンス生成テスト"""
    with patch("app.llm_processor.OpenAI", autospec=True) as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # APIキー検証用のモックを設定
        mock_client.models = MagicMock()
        mock_client.models.list = MagicMock()

        processor = LLMProcessor(model_type="gpt", api_key="test_key")

        # レスポンス生成用のモックを設定
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="テスト回答"))
        ]
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_completion
        )

        response = await processor._generate_gpt_response("テストプロンプト")
        assert response == "テスト回答"
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_claude_response():
    """Claudeモデルのレスポンス生成テスト"""
    with patch(
        "app.llm_processor.Anthropic", autospec=True
    ) as mock_anthropic_class:
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # APIキー検証用のモックを設定
        mock_client.messages = MagicMock()
        mock_validation_response = MagicMock()
        mock_client.messages.create = AsyncMock(
            return_value=mock_validation_response
        )

        processor = LLMProcessor(model_type="claude", api_key="test_key")

        # 実際のレスポンス用のモックを設定
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="テスト回答")]
        mock_client.messages.create.return_value = mock_response

        response = await processor._generate_claude_response(
            "テストプロンプト"
        )
        assert response == "テスト回答"

        # APIキー検証とメッセージ生成の両方が呼ばれたことを確認
        assert mock_client.messages.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_ollama_response():
    """Ollamaモデルのレスポンス生成テスト"""
    processor = LLMProcessor(model_type="ollama")
    with patch.object(
        processor.client, "chat", new_callable=AsyncMock
    ) as mock_chat:
        mock_chat.return_value = {"message": {"content": "テスト回答"}}
        response = await processor._generate_ollama_response(
            "テストプロンプト"
        )
        assert response == "テスト回答"
        mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_handling(processor, sample_context):
    """APIエラーのハンドリングテスト"""
    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.side_effect = Exception("API Error")
        with pytest.raises(LLMProcessorError) as exc_info:
            await processor.generate_response("テストクエリ", sample_context)
        assert "回答生成に失敗" in str(exc_info.value)


@pytest.mark.asyncio
async def test_model_switching():
    """モデル切り替えのテスト"""
    # 各モデルでの初期化と応答生成をテスト
    models = ["gemini", "gpt", "claude", "ollama"]
    api_key = "test_key"

    for model_type in models:
        if model_type == "gemini":
            with patch.object(genai, "GenerativeModel") as mock_model:
                mock_instance = MagicMock()
                mock_model.return_value = mock_instance
                mock_instance.generate_content_async = AsyncMock(
                    return_value=MagicMock(text=f"{model_type}の応答")
                )

                processor = LLMProcessor(
                    model_type=model_type, api_key=api_key
                )
                response = await processor._generate_model_response("テスト")
                assert f"{model_type}の応答" in response
                mock_instance.generate_content_async.assert_called_once()

        elif model_type == "gpt":
            with patch(
                "app.llm_processor.OpenAI", autospec=True
            ) as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client

                # APIキー検証用のモックを設定
                mock_client.models = MagicMock()
                mock_client.models.list = MagicMock()

                processor = LLMProcessor(
                    model_type=model_type, api_key=api_key
                )

                # レスポンス生成用のモックを設定
                mock_completion = MagicMock()
                mock_completion.choices = [
                    MagicMock(message=MagicMock(content=f"{model_type}の応答"))
                ]
                mock_client.chat.completions.create = AsyncMock(
                    return_value=mock_completion
                )

                response = await processor._generate_model_response("テスト")
                assert f"{model_type}の応答" in response
                mock_client.chat.completions.create.assert_called_once()

        elif model_type == "claude":
            with patch(
                "app.llm_processor.Anthropic", autospec=True
            ) as mock_anthropic_class:
                mock_client = MagicMock()
                mock_anthropic_class.return_value = mock_client

                # APIキー検証用のモックを設定
                mock_client.messages = MagicMock()
                mock_validation_response = MagicMock()
                mock_client.messages.create = AsyncMock(
                    return_value=mock_validation_response
                )

                processor = LLMProcessor(
                    model_type=model_type, api_key=api_key
                )

                # 実際のレスポンス用のモックを設定
                mock_response = MagicMock()
                mock_response.content = [MagicMock(text=f"{model_type}の応答")]
                mock_client.messages.create.return_value = mock_response

                response = await processor._generate_model_response("テスト")
                assert f"{model_type}の応答" in response

                # APIキー検証とメッセージ生成の両方が呼ばれたことを確認
                assert mock_client.messages.create.call_count == 2

        else:  # ollama
            with patch.object(
                ollama, "chat", new_callable=AsyncMock
            ) as mock_chat:
                mock_chat.return_value = {
                    "message": {"content": f"{model_type}の応答"}
                }

                processor = LLMProcessor(model_type=model_type)
                response = await processor._generate_model_response("テスト")
                assert f"{model_type}の応答" in response
                mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_prompt_length_limit():
    """プロンプトの長さ制限のテスト"""
    processor = LLMProcessor(model_type="gemini")

    # 長いコンテキストを生成
    long_context = []
    for i in range(100):
        long_context.append(
            {
                "id": str(i),
                "url": f"https://twitter.com/user/status/{i}",
                "text": "とても" * 1000,  # 非常に長いテキスト
                "created_at": str(i),
            }
        )

    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.return_value = MagicMock(text="テスト回答")

        # プロンプトが長すぎる場合はエラーを発生させる
        with pytest.raises(LLMProcessorError) as exc_info:
            await processor.generate_response("テストクエリ", long_context)
        assert "プロンプトが長すぎます" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_processing():
    """並行処理のテスト"""
    processor = LLMProcessor(model_type="gemini")

    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.return_value = MagicMock(text="テスト回答")

        # 複数のクエリを同時に処理
        queries = ["クエリ1", "クエリ2", "クエリ3", "クエリ4", "クエリ5"]
        tasks = [
            processor.generate_response(
                query, [{"text": "テスト", "url": "https://example.com"}]
            )
            for query in queries
        ]

        # 全てのタスクが正常に完了することを確認
        responses = await asyncio.gather(*tasks)
        assert len(responses) == len(queries)
        assert all(isinstance(response, str) for response in responses)


def test_memory_usage():
    """メモリ使用量のテスト"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss

    # 大量のインスタンスを生成
    processors = []
    for _ in range(100):
        processors.append(LLMProcessor(model_type="gemini"))

    # メモリ使用量の増加を確認
    gc.collect()  # 明示的にガベージコレクションを実行
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # 1インスタンスあたりの平均メモリ使用量を計算（バイト）
    avg_memory_per_instance = memory_increase / len(processors)

    # 1インスタンスあたり1MB以下であることを確認
    assert avg_memory_per_instance < 1024 * 1024, "メモリ使用量が想定より多い"


def test_error_messages():
    """エラーメッセージの詳細テスト"""
    # 無効なモデルタイプ
    with pytest.raises(LLMProcessorError) as exc_info:
        LLMProcessor(model_type="invalid")
    assert "サポートされていないモデルタイプです" in str(exc_info.value)

    # APIキーなしでの初期化
    with pytest.raises(LLMProcessorError) as exc_info:
        processor = LLMProcessor(model_type="gpt")
        processor._setup_model()
    assert "APIキーが必要です" in str(exc_info.value)

    # 無効なAPIキー
    with pytest.raises(LLMProcessorError) as exc_info:
        processor = LLMProcessor(model_type="gpt", api_key="invalid_key")
        processor._setup_model()
    assert "APIキーが無効です" in str(exc_info.value)

    # タイムアウト
    processor = LLMProcessor(model_type="gemini")
    with patch.object(
        processor.model, "generate_content_async", new_callable=AsyncMock
    ) as mock_generate:
        mock_generate.side_effect = asyncio.TimeoutError()
        with pytest.raises(LLMProcessorError) as exc_info:
            asyncio.run(
                processor.generate_response(
                    "テスト",
                    [{"text": "テスト", "url": "https://example.com"}],
                )
            )
        assert "タイムアウト" in str(exc_info.value)
