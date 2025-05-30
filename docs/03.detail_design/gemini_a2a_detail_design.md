# Gemini-2.5-Pro統合A2Aエージェント - 詳細設計書

## 1. クラス詳細設計

### 1.1 GeminiConfig クラス

```python
# app/a2a_prototype/utils/gemini_config.py

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class GeminiConfig:
    """Gemini API の設定情報を管理するデータクラス"""
    
    api_key: str
    model: str = "gemini-2.5-pro-preview-05-06"
    temperature: float = 0.7
    max_tokens: int = 1000
    safety_settings: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """設定値のバリデーション"""
        self._validate_api_key()
        self._validate_temperature()
        self._validate_max_tokens()
        self._validate_model()
    
    def _validate_api_key(self) -> None:
        """APIキーのバリデーション"""
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("API key must be a non-empty string")
        if len(self.api_key) < 10:  # 最低限の長さチェック
            raise ValueError("API key appears to be invalid (too short)")
    
    def _validate_temperature(self) -> None:
        """Temperatureパラメータのバリデーション"""
        if not isinstance(self.temperature, (int, float)):
            raise ValueError("Temperature must be a number")
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
    
    def _validate_max_tokens(self) -> None:
        """Max tokensパラメータのバリデーション"""
        if not isinstance(self.max_tokens, int):
            raise ValueError("Max tokens must be an integer")
        if not 1 <= self.max_tokens <= 8192:  # Gemini制限に基づく
            raise ValueError("Max tokens must be between 1 and 8192")
    
    def _validate_model(self) -> None:
        """モデル名のバリデーション"""
        if not self.model or not isinstance(self.model, str):
            raise ValueError("Model must be a non-empty string")
        valid_models = ["gemini-2.5-pro-preview-05-06", "gemini-1.5-pro", "gemini-1.0-pro"]
        if self.model not in valid_models:
            # 警告は出すが、新しいモデルの可能性もあるのでエラーにはしない
            import logging
            logging.warning(f"Unknown model: {self.model}. Valid models: {valid_models}")
    
    @classmethod
    def from_env(cls) -> "GeminiConfig":
        """環境変数から設定を読み込み"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-preview-05-06"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
        )
    
    def to_generation_config(self) -> Dict[str, Any]:
        """Gemini GenerationConfig形式に変換"""
        return {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
    
    def get_masked_api_key(self) -> str:
        """マスキングされたAPIキーを取得（ログ出力用）"""
        if len(self.api_key) <= 8:
            return "*" * len(self.api_key)
        return f"{self.api_key[:8]}{'*' * (len(self.api_key) - 8)}"
```

### 1.2 GeminiClient クラス

```python
# app/a2a_prototype/utils/gemini_client.py

import asyncio
import logging
from typing import Optional, Dict, Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold

from .gemini_config import GeminiConfig

logger = logging.getLogger(__name__)

class GeminiAPIError(Exception):
    """Gemini API 関連のエラー"""
    pass

class GeminiClient:
    """Gemini AI API のクライアントWrapper"""
    
    def __init__(self, config: GeminiConfig) -> None:
        """
        Args:
            config: Gemini API設定
        """
        self.config = config
        self._model: Optional[genai.GenerativeModel] = None
        self._initialized = False
        self._setup_client()
    
    def _setup_client(self) -> None:
        """Geminiクライアントをセットアップ"""
        try:
            # API認証設定
            genai.configure(api_key=self.config.api_key)
            
            # Safety settings
            safety_settings = self._get_safety_settings()
            
            # モデル初期化
            self._model = genai.GenerativeModel(
                model_name=self.config.model,
                generation_config=GenerationConfig(**self.config.to_generation_config()),
                safety_settings=safety_settings
            )
            
            self._initialized = True
            logger.info(f"Gemini client initialized: {self.config.model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Client initialization failed: {e}") from e
    
    def _get_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """セーフティ設定を取得"""
        if self.config.safety_settings:
            return self.config.safety_settings
        
        # デフォルトのセーフティ設定
        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_FEW,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_FEW,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_FEW,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_FEW,
        }
    
    async def generate_response(self, prompt: str) -> str:
        """
        Geminiからレスポンスを生成
        
        Args:
            prompt: 入力プロンプト
            
        Returns:
            生成されたレスポンステキスト
            
        Raises:
            GeminiAPIError: API呼び出しに失敗した場合
        """
        if not self._initialized or not self._model:
            raise GeminiAPIError("Client not properly initialized")
        
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            # 非同期でAPI呼び出し
            response = await asyncio.to_thread(
                self._model.generate_content,
                prompt.strip()
            )
            
            if not response.text:
                logger.warning("Empty response from Gemini API")
                return "申し訳ございませんが、回答を生成できませんでした。"
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"Failed to generate response: {e}") from e
    
    async def generate_response_with_timeout(self, prompt: str, timeout: float = 5.0) -> str:
        """
        タイムアウト付きでレスポンスを生成
        
        Args:
            prompt: 入力プロンプト
            timeout: タイムアウト時間（秒）
            
        Returns:
            生成されたレスポンステキスト
        """
        try:
            return await asyncio.wait_for(
                self.generate_response(prompt),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Gemini API timeout after {timeout} seconds")
            return "応答時間が長すぎます。より簡潔な質問でお試しください。"
        except GeminiAPIError:
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。"
    
    async def health_check(self) -> bool:
        """
        Gemini API の接続確認
        
        Returns:
            接続状態（True=正常, False=異常）
        """
        if not self._initialized:
            return False
            
        try:
            response = await self.generate_response_with_timeout(
                "Hello", timeout=3.0
            )
            return bool(response and len(response) > 0 and "申し訳ございません" not in response)
            
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False
    
    def get_client_info(self) -> Dict[str, Any]:
        """クライアント情報を取得"""
        return {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "initialized": self._initialized,
            "api_key_masked": self.config.get_masked_api_key()
        }
```

### 1.3 GeminiA2AAgent クラス

```python
# app/a2a_prototype/agents/gemini_agent.py

import logging
from typing import List, Dict, Any

from a2a.types import AgentSkill

from ..utils.config import AgentConfig
from ..utils.gemini_client import GeminiClient, GeminiAPIError
from ..utils.gemini_config import GeminiConfig
from .base_agent import BaseA2AAgent

logger = logging.getLogger(__name__)

class GeminiA2AAgent(BaseA2AAgent):
    """Gemini 2.5 Pro を使用したA2Aエージェント"""
    
    # クラス定数
    MAX_CONTEXT_MESSAGES = 20  # 会話履歴の最大保持数（10往復分）
    MAX_INPUT_LENGTH = 10000   # ユーザー入力の最大長
    
    def __init__(self, config: AgentConfig, gemini_config: GeminiConfig) -> None:
        """
        Args:
            config: A2Aエージェント設定
            gemini_config: Gemini API設定
        """
        super().__init__(config)
        self.gemini_config = gemini_config
        self.gemini_client = GeminiClient(gemini_config)
        self.conversation_context: List[str] = []
        
        # エージェント固有のログ設定
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.logger.info(f"Gemini agent initialized with model: {gemini_config.model}")
    
    def get_skills(self) -> List[AgentSkill]:
        """エージェントのスキル一覧を取得"""
        return [
            AgentSkill(
                id="chat",
                name="intelligent_chat",
                description="Have an intelligent conversation using Gemini 2.5 Pro",
                tags=["conversation", "ai", "general"],
            ),
            AgentSkill(
                id="qa", 
                name="question_answering",
                description="Answer questions using advanced AI capabilities",
                tags=["qa", "knowledge", "research"],
            ),
            AgentSkill(
                id="help",
                name="help_assistant", 
                description="Provide help and guidance",
                tags=["help", "assistance", "guide"],
            ),
        ]
    
    async def process_user_input(self, user_input: str) -> str:
        """
        ユーザー入力をGemini 2.5 Proで処理
        
        Args:
            user_input: ユーザーからの入力テキスト
            
        Returns:
            Geminiが生成した応答テキスト
        """
        try:
            # 入力バリデーション
            sanitized_input = self._sanitize_user_input(user_input)
            
            # 特別なコマンドの処理
            if self._is_help_command(sanitized_input):
                return self._get_help_message()
            
            elif self._is_clear_command(sanitized_input):
                return self._clear_conversation_context()
            
            elif self._is_status_command(sanitized_input):
                return await self._get_status_message()
            
            # 通常の対話処理
            prompt = self._build_conversation_prompt(sanitized_input)
            response = await self.gemini_client.generate_response_with_timeout(prompt)
            
            # 会話履歴を更新
            self._update_conversation_context(sanitized_input, response)
            
            return response
            
        except ValueError as e:
            self.logger.warning(f"Input validation error: {e}")
            return f"入力エラー: {e}"
            
        except GeminiAPIError as e:
            self.logger.error(f"Gemini API error: {e}")
            return "申し訳ございません。AIサービスに一時的な問題が発生しています。しばらく時間をおいて再度お試しください。"
            
        except Exception as e:
            self.logger.error(f"Unexpected error in process_user_input: {e}")
            return "予期しない問題が発生しました。しばらく時間をおいて再度お試しください。"
    
    def _sanitize_user_input(self, user_input: str) -> str:
        """ユーザー入力のサニタイズ"""
        if not user_input:
            raise ValueError("入力が空です")
        
        sanitized = user_input.strip()
        
        if len(sanitized) > self.MAX_INPUT_LENGTH:
            raise ValueError(f"入力が長すぎます（最大{self.MAX_INPUT_LENGTH}文字）")
        
        return sanitized
    
    def _is_help_command(self, input_text: str) -> bool:
        """ヘルプコマンドかどうか判定"""
        return input_text.lower() in ["help", "?", "ヘルプ"]
    
    def _is_clear_command(self, input_text: str) -> bool:
        """クリアコマンドかどうか判定"""
        return input_text.lower() in ["clear", "クリア", "リセット"]
    
    def _is_status_command(self, input_text: str) -> bool:
        """ステータスコマンドかどうか判定"""
        return input_text.lower() in ["status", "ステータス", "状態"]
    
    def _build_conversation_prompt(self, user_input: str) -> str:
        """会話履歴を考慮したプロンプトを構築"""
        base_prompt = (
            "あなたは親切で知識豊富なAIアシスタントです。"
            "ユーザーの質問に対して、正確で有用な回答を提供してください。"
            "回答は分かりやすく、適度な長さで行ってください。\n\n"
        )
        
        # 会話履歴があれば追加（最新6件=3往復分）
        if self.conversation_context:
            recent_context = self.conversation_context[-6:]
            conversation_history = "\n".join(recent_context)
            base_prompt += f"会話履歴:\n{conversation_history}\n\n"
        
        base_prompt += f"ユーザー: {user_input}\nアシスタント: "
        
        return base_prompt
    
    def _update_conversation_context(self, user_input: str, ai_response: str) -> None:
        """会話履歴を更新"""
        self.conversation_context.extend([
            f"User: {user_input}",
            f"Assistant: {ai_response}"
        ])
        
        # 上限を超えた場合は古い履歴を削除
        if len(self.conversation_context) > self.MAX_CONTEXT_MESSAGES:
            self.conversation_context = self.conversation_context[-self.MAX_CONTEXT_MESSAGES:]
    
    def _clear_conversation_context(self) -> str:
        """会話履歴をクリア"""
        self.conversation_context.clear()
        return "✅ 会話履歴をクリアしました。新しい会話を始めましょう！"
    
    async def _get_status_message(self) -> str:
        """ステータスメッセージを生成"""
        health = await self.gemini_client.health_check()
        client_info = self.gemini_client.get_client_info()
        
        return (
            f"🤖 {self.config.name}\n"
            f"📡 URL: {self.config.url}\n"
            f"🧠 Model: {client_info['model']}\n"
            f"🌡️ Temperature: {client_info['temperature']}\n"
            f"📝 Max Tokens: {client_info['max_tokens']}\n"
            f"💚 Status: {'✅ OK' if health else '❌ ERROR'}\n"
            f"💬 Context: {len(self.conversation_context)} messages\n"
            f"🔑 API Key: {client_info['api_key_masked']}"
        )
    
    def _get_help_message(self) -> str:
        """ヘルプメッセージを生成"""
        return (
            f"🤖 **{self.config.name}** - Gemini 2.5 Pro搭載エージェント\n\n"
            "📝 **使い方:**\n"
            "• 質問やメッセージを自由に送信してください\n"
            "• `status` - エージェントの状態確認\n"
            "• `clear` - 会話履歴をクリア\n"
            "• `help` - このヘルプメッセージを表示\n\n"
            "🧠 **特徴:**\n"
            "• Google Gemini 2.5 Proによる高度な対話\n"
            "• 会話履歴を考慮した文脈理解\n"
            "• A2Aプロトコル完全準拠\n"
            "• リアルタイム応答\n\n"
            "💡 **技術仕様:**\n"
            f"• Model: {self.gemini_config.model}\n"
            f"• Temperature: {self.gemini_config.temperature}\n"
            f"• Max Context: {self.MAX_CONTEXT_MESSAGES // 2} 往復\n\n"
            "何でもお気軽にお聞かせください！✨"
        )
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """エージェントの統計情報を取得"""
        return {
            "conversation_messages": len(self.conversation_context),
            "max_context_messages": self.MAX_CONTEXT_MESSAGES,
            "gemini_model": self.gemini_config.model,
            "gemini_temperature": self.gemini_config.temperature,
            "skills_count": len(self.get_skills()),
        }
```

## 2. ヘルパー関数設計

### 2.1 エージェント作成ヘルパー

```python
# app/a2a_prototype/agents/__init__.py への追加

from .gemini_agent import GeminiA2AAgent

def create_gemini_agent(port: int = 8004, **kwargs) -> GeminiA2AAgent:
    """
    Geminiエージェントを作成
    
    Args:
        port: エージェントのポート番号
        **kwargs: 追加の設定パラメータ
        
    Returns:
        設定済みのGeminiA2AAgent
        
    Raises:
        ValueError: 環境変数が不足している場合
        GeminiConfigError: Gemini設定に問題がある場合
    """
    from ..utils.config import AgentConfig
    from ..utils.gemini_config import GeminiConfig
    
    # A2Aエージェント設定
    agent_config = AgentConfig(
        name=kwargs.get("name", "gemini-chat-agent"),
        description=kwargs.get("description", "Advanced conversational AI agent powered by Gemini 2.5 Pro"),
        url=f"http://localhost:{port}",
        port=port,
        version=kwargs.get("version", "1.0.0")
    )
    
    # Gemini設定（環境変数から読み込み）
    gemini_config = GeminiConfig.from_env()
    
    # カスタム設定の上書き
    if "temperature" in kwargs:
        gemini_config.temperature = kwargs["temperature"]
    if "max_tokens" in kwargs:
        gemini_config.max_tokens = kwargs["max_tokens"]
    if "model" in kwargs:
        gemini_config.model = kwargs["model"]
    
    return GeminiA2AAgent(agent_config, gemini_config)
```

### 2.2 実行スクリプト

```python
# scripts/run_gemini_agent.py

"""
Gemini A2A Agent 実行スクリプト
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.a2a_prototype.agents import create_gemini_agent

def setup_logging() -> None:
    """ログ設定をセットアップ"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('gemini_agent.log')
        ]
    )

async def main() -> None:
    """Geminiエージェントを起動"""
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 環境変数確認
        if not os.getenv("GEMINI_API_KEY"):
            print("❌ GEMINI_API_KEY environment variable is required")
            print("🔧 Set it with: export GEMINI_API_KEY='your-api-key'")
            print("💡 Get your API key from: https://makersuite.google.com/app/apikey")
            return
        
        # Geminiエージェント作成
        agent = create_gemini_agent(port=8004)
        
        print(f"🚀 Starting {agent.config.name}...")
        print(f"📡 URL: {agent.config.url}")
        print(f"🧠 Model: {agent.gemini_config.model}")
        print(f"🌡️ Temperature: {agent.gemini_config.temperature}")
        print(f"💡 Test at: {agent.config.url}/.well-known/agent.json")
        print(f"📊 Health check: {agent.config.url}/health")
        print("\n💬 Ready for A2A conversations!")
        
        # ヘルスチェック実行
        health = await agent.gemini_client.health_check()
        if health:
            print("✅ Gemini API connection verified")
        else:
            print("⚠️ Warning: Gemini API health check failed")
        
        # エージェント起動
        agent.run_agent(host="0.0.0.0", port=8004)
        
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user.")
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        print(f"❌ Error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. エラーハンドリング詳細

### 3.1 カスタム例外クラス

```python
# app/a2a_prototype/exceptions.py

"""カスタム例外クラス定義"""

class GeminiA2AError(Exception):
    """Gemini A2A エージェント関連のベースエラー"""
    pass

class GeminiConfigError(GeminiA2AError):
    """Gemini設定関連のエラー"""
    pass

class GeminiAPIError(GeminiA2AError):
    """Gemini API通信関連のエラー"""
    pass

class A2AProtocolError(GeminiA2AError):
    """A2Aプロトコル関連のエラー"""
    pass
```

## 4. テストデータ・フィクスチャ設計

### 4.1 テスト設定

```python
# tests/fixtures/gemini_fixtures.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.a2a_prototype.utils.gemini_config import GeminiConfig
from app.a2a_prototype.utils.config import AgentConfig
from app.a2a_prototype.utils.gemini_client import GeminiClient

@pytest.fixture
def test_gemini_config():
    """テスト用Gemini設定"""
    return GeminiConfig(
        api_key="test-api-key-12345678",
        model="gemini-2.5-pro-preview-05-06",
        temperature=0.5,
        max_tokens=500
    )

@pytest.fixture
def test_agent_config():
    """テスト用エージェント設定"""
    return AgentConfig(
        name="test-gemini-agent",
        description="Test Gemini agent",
        url="http://localhost:8999",
        port=8999
    )

@pytest.fixture
def mock_gemini_client():
    """モックされたGeminiClient"""
    client = AsyncMock(spec=GeminiClient)
    client.generate_response.return_value = "Test response from Gemini"
    client.generate_response_with_timeout.return_value = "Test response with timeout"
    client.health_check.return_value = True
    client.get_client_info.return_value = {
        "model": "gemini-2.5-pro-preview-05-06",
        "temperature": 0.7,
        "max_tokens": 1000,
        "initialized": True,
        "api_key_masked": "test-api********"
    }
    return client

@pytest.fixture 
def mock_genai():
    """モックされたgoogle.generativeai"""
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model:
        
        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini response"
        
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        yield {
            'configure': mock_configure,
            'model_class': mock_model,
            'model_instance': mock_model_instance,
            'response': mock_response
        }
```

---

**作成日**: 2025-01-XX  
**バージョン**: 1.0  
**承認**: TBD 