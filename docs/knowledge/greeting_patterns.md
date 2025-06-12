# 挨拶タスク実装パターン

## 概要

このドキュメントは、挨拶タスクの実装における標準パターンとベストプラクティスを記録します。時間帯別の挨拶、状況別の挨拶パターン、およびエラーハンドリングについて定義します。

## 時間帯別挨拶パターン

### 朝の挨拶（5:00 - 11:59）

```python
morning_greetings = [
    "おはようございます！",
    "Good morning!",
    "朝ですね。今日も一日頑張りましょう！",
    "おはよう！素敵な一日になりますように。"
]

# 時間帯判定
def is_morning(hour: int) -> bool:
    return 5 <= hour < 12
```

### 昼の挨拶（12:00 - 17:59）

```python
afternoon_greetings = [
    "こんにちは！",
    "Good afternoon!",
    "午後も頑張っていきましょう！",
    "こんにちは。調子はいかがですか？"
]

# 時間帯判定
def is_afternoon(hour: int) -> bool:
    return 12 <= hour < 18
```

### 夜の挨拶（18:00 - 4:59）

```python
evening_greetings = [
    "こんばんは！",
    "Good evening!",
    "お疲れ様です！",
    "こんばんは。今日も一日お疲れ様でした。"
]

# 時間帯判定
def is_evening(hour: int) -> bool:
    return hour >= 18 or hour < 5
```

## 状況別挨拶パターン

### 初回挨拶

```python
first_meeting_patterns = {
    "formal": [
        "はじめまして。よろしくお願いいたします。",
        "Nice to meet you. I'm happy to help you.",
        "初めてお会いしますね。何かお手伝いできることがありましたら、お申し付けください。"
    ],
    "casual": [
        "はじめまして！よろしく！",
        "Hi there! Nice to meet you!",
        "初めまして〜！気軽に話しかけてくださいね。"
    ]
}
```

### 再会挨拶

```python
return_greeting_patterns = {
    "short_absence": [  # 数時間〜1日以内
        "おかえりなさい！",
        "Welcome back!",
        "また会えて嬉しいです！"
    ],
    "long_absence": [  # 数日以上
        "お久しぶりです！",
        "It's been a while! How have you been?",
        "しばらくぶりですね。お元気でしたか？"
    ]
}
```

### 特殊な状況

```python
special_situations = {
    "birthday": [
        "お誕生日おめでとうございます！🎉",
        "Happy Birthday! 🎂",
        "素敵な一年になりますように！"
    ],
    "new_year": [
        "あけましておめでとうございます！",
        "Happy New Year!",
        "今年もよろしくお願いします。"
    ],
    "holiday": [
        "良い休日をお過ごしください！",
        "Enjoy your holiday!",
        "ゆっくり休んでくださいね。"
    ]
}
```

## エラーハンドリングパターン

### 基本的なエラーハンドリング

```python
class GreetingError(Exception):
    """挨拶処理に関する基本例外クラス"""
    pass

class TimeZoneError(GreetingError):
    """タイムゾーン関連のエラー"""
    pass

class LocalizationError(GreetingError):
    """言語・地域設定関連のエラー"""
    pass
```

### エラー処理の実装例

```python
def generate_greeting(context: dict) -> str:
    """
    コンテキストに基づいて適切な挨拶を生成
    
    Args:
        context: {
            'time': datetime,
            'language': str,
            'user_info': dict,
            'situation': str
        }
    
    Returns:
        str: 生成された挨拶文
    
    Raises:
        TimeZoneError: タイムゾーン情報が不正な場合
        LocalizationError: 言語設定が未対応の場合
    """
    try:
        # タイムゾーン処理
        if not context.get('time'):
            # デフォルトは現在時刻を使用
            context['time'] = datetime.now()
        
        # 言語設定の検証
        supported_languages = ['ja', 'en']
        language = context.get('language', 'ja')
        if language not in supported_languages:
            raise LocalizationError(f"Unsupported language: {language}")
        
        # 時間帯の判定
        hour = context['time'].hour
        
        # 挨拶の生成
        if is_morning(hour):
            greeting_pool = morning_greetings
        elif is_afternoon(hour):
            greeting_pool = afternoon_greetings
        else:
            greeting_pool = evening_greetings
        
        # ランダムまたはコンテキストベースで選択
        return select_greeting(greeting_pool, context)
        
    except TimeZoneError as e:
        # タイムゾーンエラーの場合はデフォルト挨拶
        logger.warning(f"TimeZone error: {e}, using default greeting")
        return "こんにちは！"  # フォールバック
        
    except LocalizationError as e:
        # 言語エラーの場合は英語でフォールバック
        logger.warning(f"Localization error: {e}, falling back to English")
        return "Hello!"
        
    except Exception as e:
        # 予期しないエラー
        logger.error(f"Unexpected error in greeting generation: {e}")
        return "Hello!"  # 最も安全なフォールバック
```

### リトライパターン

```python
from typing import Optional
import time

def greeting_with_retry(
    context: dict, 
    max_retries: int = 3,
    retry_delay: float = 0.5
) -> Optional[str]:
    """
    リトライ機能付き挨拶生成
    
    Args:
        context: 挨拶生成用コンテキスト
        max_retries: 最大リトライ回数
        retry_delay: リトライ間隔（秒）
    
    Returns:
        Optional[str]: 生成された挨拶、失敗時はNone
    """
    for attempt in range(max_retries):
        try:
            return generate_greeting(context)
        except (TimeZoneError, LocalizationError) as e:
            if attempt < max_retries - 1:
                logger.info(f"Retry {attempt + 1}/{max_retries} after error: {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                return None
    
    return None
```

## ベストプラクティス

### 1. コンテキストの活用

```python
def contextual_greeting(user_context: dict) -> str:
    """
    ユーザーコンテキストを考慮した挨拶生成
    
    考慮要素:
    - 時間帯
    - ユーザーの言語設定
    - 前回のインタラクション
    - 特別な日（誕生日、祝日など）
    - ユーザーの好み
    """
    # 実装例は上記参照
```

### 2. 多様性の確保

- 同じ挨拶の繰り返しを避ける
- ユーザーの履歴を記録して多様性を保つ
- ランダム性と予測可能性のバランス

### 3. 文化的配慮

```python
cultural_considerations = {
    "ja": {
        "formal_suffix": "さん",
        "time_sensitive": True,  # 時間帯による挨拶の区別が重要
        "bow_emoji": "🙇"
    },
    "en": {
        "formal_prefix": "Mr./Ms.",
        "time_sensitive": False,  # 時間帯の区別は柔軟
        "wave_emoji": "👋"
    }
}
```

### 4. パフォーマンス考慮

```python
# 挨拶プールのキャッシュ
from functools import lru_cache

@lru_cache(maxsize=128)
def get_greeting_pool(time_of_day: str, language: str) -> list:
    """挨拶プールをキャッシュして高速化"""
    # 実装
```

## テストパターン

### ユニットテスト例

```python
import pytest
from datetime import datetime

class TestGreetingPatterns:
    
    def test_morning_greeting(self):
        """朝の挨拶が正しく生成されることを確認"""
        context = {
            'time': datetime(2024, 1, 1, 8, 0),  # 8:00 AM
            'language': 'ja'
        }
        greeting = generate_greeting(context)
        assert any(morning in greeting for morning in morning_greetings)
    
    def test_timezone_error_handling(self):
        """タイムゾーンエラーが適切に処理されることを確認"""
        context = {
            'time': None,
            'timezone': 'invalid/timezone'
        }
        greeting = generate_greeting(context)
        assert greeting in ["こんにちは！", "Hello!"]  # フォールバック確認
    
    @pytest.mark.parametrize("hour,expected_period", [
        (7, "morning"),
        (14, "afternoon"),
        (20, "evening"),
        (2, "evening")
    ])
    def test_time_period_detection(self, hour, expected_period):
        """時間帯判定が正しく動作することを確認"""
        # 実装
```

## まとめ

挨拶タスクの実装においては、以下の要素が重要です：

1. **時間帯への適応**: ユーザーのローカルタイムに基づいた適切な挨拶
2. **文化的配慮**: 言語と文化に応じた挨拶の選択
3. **エラー耐性**: 様々なエラー状況でも適切にフォールバック
4. **多様性**: 繰り返しを避け、自然な会話を実現
5. **テスト可能性**: 全てのパターンが適切にテストされていること

これらのパターンを活用することで、より自然で親しみやすい挨拶機能を実装できます。