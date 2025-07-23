# タイムアウト設定について

## 現在の実装状況

**タイムアウトは既に設定可能です！**

### 設定方法

1. **環境変数で設定**
   ```bash
   export LLM_TIMEOUT=120  # 120秒に設定
   ```

2. **設定ファイルで設定**
   ```yaml
   # config.yaml
   llm:
     timeout: 120  # 秒単位
   ```

3. **コード内で設定**
   ```python
   from config import get_config
   
   config = get_config()
   config.llm.timeout = 120  # 120秒に設定
   ```

### 現在のデフォルト値

- `LLMConfig.timeout`: **60秒**（`src/config/config.py`で定義）

### 設定が適用される場所

`src/utils/llm_factory.py`でLLMインスタンス作成時に適用：

```python
# Gemini
ChatGoogleGenerativeAI(
    timeout=kwargs.get("timeout", config.llm.timeout),  # ここで適用
    ...
)

# OpenAI
ChatOpenAI(
    timeout=kwargs.get("timeout", config.llm.timeout),  # ここで適用
    ...
)

# Anthropic
ChatAnthropic(
    timeout=kwargs.get("timeout", config.llm.timeout),  # ここで適用
    ...
)
```

## プロダクション運用時の設定例

### 1. 通常のAPIエンドポイント
```bash
# 環境変数で設定（推奨）
export LLM_TIMEOUT=30  # 高速レスポンスが必要
```

### 2. バッチ処理や詳細分析
```bash
export LLM_TIMEOUT=300  # 5分まで待つ
```

### 3. 開発・テスト環境
```bash
export LLM_TIMEOUT=120  # 余裕を持った設定
```

## 結論

- **テストはそのままでOK** - プロダクションで柔軟に変更可能
- **環境変数で簡単に調整** - デプロイ時に設定変更
- **用途に応じて最適化** - APIは短め、バッチは長めなど

既に必要な仕組みは実装済みです！