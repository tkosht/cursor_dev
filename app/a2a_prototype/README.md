# A2A Protocol Investigation - Prototype

このディレクトリには、Google公式a2a-sdk v0.2.4を使用したA2A（Agent-to-Agent）プロトコルの実機調査・検証用プロトタイプが含まれています。

## 📁 プロジェクト構造

```
./
├── examples/                        # 🆕 動作確認・デモ用スクリプト
│   ├── a2a_basic_check.py              # A2A SDK基本動作確認
│   └── simple_agent_demo.py            # SimpleTestAgentデモ
├── tests/                           # 🆕 TDD準拠のpytestテスト
│   ├── conftest.py                     # pytest共通設定・フィクスチャ
│   ├── unit/                           # 単体テスト（高速・独立）
│   │   ├── test_types/                 # a2a.types テスト
│   │   │   └── test_agent_skill.py     # AgentSkill TDDテスト
│   │   └── test_agents/                # エージェント単体テスト
│   │       └── test_simple_agent.py    # SimpleTestAgent TDDテスト
│   ├── integration/                    # 統合テスト（中速・依存あり）
│   └── e2e/                           # E2Eテスト（低速・完全シナリオ）
├── app/a2a_prototype/               # アプリケーションコード
│   ├── agents/                         # エージェント実装
│   │   ├── base_agent.py               # 基底エージェントクラス
│   │   └── simple_agent.py             # SimpleTestAgent実装
│   └── utils/                          # ユーティリティ
│       └── config.py                   # エージェント設定管理
└── docs/                            # ドキュメント
    ├── a2a_implementation_guide.md     # 技術実装ガイド
    └── development_rules/              # 開発ルール・ガイドライン
        └── tdd_implementation_guide.md # TDD実践ガイド
```

## 🔄 ファイル名整理について

### 整理前（問題があった構造）

```
❌ app/a2a_prototype/simple_test.py     # 動作確認だがpytestっぽい名前
❌ app/a2a_prototype/test_simple_agent.py # pytestテストだが配置場所が不適切
```

**問題点**:
- pytest標準の命名規則に非準拠
- 動作確認スクリプトとpytestテストが混在
- TDD実践になっていない甘いテスト
- アプリケーションディレクトリにテストファイルが配置

### 整理後（適切な構造）

```
✅ examples/a2a_basic_check.py          # 明確に動作確認用
✅ examples/simple_agent_demo.py        # 明確にデモ用
✅ tests/unit/test_types/test_agent_skill.py     # TDD準拠のpytestテスト
✅ tests/unit/test_agents/test_simple_agent.py   # TDD準拠のpytestテスト
```

**改善点**:
- 役割が明確な命名・配置
- pytest標準ディレクトリ構造準拠
- TDD（Test Driven Development）実践
- 単体・統合・E2Eテストの階層化

## 🚀 クイックスタート

### 1. 基本動作確認（手動テスト）

```bash
# A2A SDK基本動作確認
python examples/a2a_basic_check.py

# SimpleTestAgentデモ
python examples/simple_agent_demo.py
```

### 2. TDD準拠のテスト実行

```bash
# 単体テストのみ（高速）
poetry run pytest tests/unit/ -v

# 全テスト実行
poetry run pytest tests/ -v

# カバレッジ付きテスト実行
poetry run pytest tests/ --cov=src --cov-report=html

# テストカテゴリ別実行
poetry run pytest tests/unit/ -m unit
poetry run pytest tests/integration/ -m integration
```

## 🎯 TDD実践について

このプロジェクトでは **Test Driven Development (TDD)** を厳格に実践しています：

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通すための最小限の実装
3. **Refactor**: コードを改善しつつテストが通ることを確認

詳細は [`docs/development_rules/tdd_implementation_guide.md`](../../docs/development_rules/tdd_implementation_guide.md) を参照してください。

## 📊 テスト品質指標

- **単体テスト**: 最低90%、目標95% カバレッジ
- **統合テスト**: 主要パス100%
- **E2Eテスト**: クリティカルパス100%
- **実行時間**: 単体テスト<10秒、統合テスト<30秒、E2E<120秒

## 🔧 開発ワークフロー

### 新機能追加時

```bash
# 1. テストファースト：失敗するテストを書く
echo "def test_new_feature(): assert False" >> tests/unit/test_new_feature.py

# 2. テスト実行（Red）
poetry run pytest tests/unit/test_new_feature.py

# 3. 最小実装（Green）
# 実装コードを作成してテストを通す

# 4. リファクタリング（Refactor）
# コードを改善しつつテストが通ることを確認
```

### バグ修正時

```bash
# 1. 再現テストを先に書く
# 2. テストが失敗することを確認
# 3. バグを修正
# 4. テストが通ることを確認
```

## 💡 学習事項

このプロジェクトから得られた重要な学習事項は以下にまとめられています：

- [`memory-bank/a2a_implementation_lessons_learned.md`](../../memory-bank/a2a_implementation_lessons_learned.md)
- A2A公式SDKの正確なAPI仕様確認方法
- Pydanticバリデーションエラーの体系的解析
- TDD実践の重要性と具体的手法

## 🔗 関連ドキュメント

- [A2A実装技術ガイド](../../docs/a2a_implementation_guide.md)
- [TDD実践ガイドライン](../../docs/development_rules/tdd_implementation_guide.md)
- [プロジェクト学習事項](../../memory-bank/a2a_implementation_lessons_learned.md)

---

**注意**: このプロトタイプは調査・学習目的です。本番環境での使用前に追加の検証・テストが必要です。 