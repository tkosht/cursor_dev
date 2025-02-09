"""LLMProcessorのテスト"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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
    with patch.object(processor.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(2)
            return MagicMock(text="遅い応答")
        mock_generate.side_effect = slow_response
        with pytest.raises(LLMProcessorError) as exc_info:
            await processor.generate_response("テストクエリ", sample_context, timeout=1)
        assert "タイムアウト" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_gemini_response(processor):
    """Geminiモデルのレスポンス生成テスト"""
    with patch.object(processor.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = MagicMock(text="テスト回答")
        response = await processor._generate_gemini_response("テストプロンプト")
        assert response == "テスト回答"
        mock_generate.assert_called_once_with("テストプロンプト")


@pytest.mark.asyncio
async def test_generate_gpt_response():
    """GPTモデルのレスポンス生成テスト"""
    processor = LLMProcessor(model_type="gpt", api_key="test_key")
    with patch.object(processor.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="テスト回答"))]
        )
        response = await processor._generate_gpt_response("テストプロンプト")
        assert response == "テスト回答"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_claude_response():
    """Claudeモデルのレスポンス生成テスト"""
    processor = LLMProcessor(model_type="claude", api_key="test_key")
    with patch.object(processor.client, 'messages', create=True) as mock_messages:
        mock_messages.create = AsyncMock(
            return_value=MagicMock(content=[MagicMock(text="テスト回答")])
        )
        response = await processor._generate_claude_response("テストプロンプト")
        assert response == "テスト回答"
        mock_messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_ollama_response():
    """Ollamaモデルのレスポンス生成テスト"""
    processor = LLMProcessor(model_type="ollama")
    with patch.object(processor.client, 'chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = {'message': {'content': "テスト回答"}}
        response = await processor._generate_ollama_response("テストプロンプト")
        assert response == "テスト回答"
        mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_handling(processor, sample_context):
    """APIエラーのハンドリングテスト"""
    with patch.object(processor.model, 'generate_content_async', new_callable=AsyncMock) as mock_generate:
        mock_generate.side_effect = Exception("API Error")
        with pytest.raises(LLMProcessorError) as exc_info:
            await processor.generate_response("テストクエリ", sample_context)
        assert "回答生成に失敗" in str(exc_info.value) 