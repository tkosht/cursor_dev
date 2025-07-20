# Model Selection Recommendations for AI Agents

## 🚨 重要：エージェント用モデル選択ガイドライン

### 推奨モデル（2025年7月時点）

#### 1. **標準エージェント用モデル**
- **推奨**: `gpt-4.1`
- **理由**: 
  - 最新の機能と高い精度
  - エージェントタスクに最適化
  - コストパフォーマンスが良好

#### 2. **軽量タスク用モデル**
- **推奨**: `gpt-4.1-mini`
- **理由**:
  - 簡単なタスクに十分な性能
  - コスト効率が高い
  - レスポンスが高速

### ❌ 非推奨モデル

#### 1. **gpt-4**
- **問題点**:
  - 古いモデルで精度が低い
  - 高額（新しいモデルより高い）
  - 最新機能をサポートしない
- **代替**: `gpt-4.1` を使用

#### 2. **gpt-3.5-turbo**
- **問題点**:
  - エージェントとしてもはや機能しない
  - 複雑なタスクの処理能力が不足
  - ツール使用の信頼性が低い
- **代替**: `gpt-4.1-mini` を使用

### 📋 実装時のチェックリスト

```python
# ✅ 正しい例
agent = create_react_agent(
    ChatOpenAI(model="gpt-4.1"),  # 標準エージェント
    tools=[...],
    system_message="..."
)

lightweight_agent = create_react_agent(
    ChatOpenAI(model="gpt-4.1-mini"),  # 軽量タスク
    tools=[...],
    system_message="..."
)

# ❌ 避けるべき例
# ChatOpenAI(model="gpt-4")  # 古くて高額
# ChatOpenAI(model="gpt-3.5-turbo")  # エージェントとして機能しない
```

### 🔄 更新履歴
- 2025-07-20: 初版作成
  - gpt-4 → gpt-4.1 への移行を推奨
  - gpt-3.5-turbo → gpt-4.1-mini への移行を推奨

### 📚 関連ドキュメント
- `/docs/langgraph-implementation-guide.md` - LangGraph実装ガイド（モデル更新済み）