# Multi-Agent Article Review System

記事の品質を多角的に評価し、改善提案を生成するマルチエージェントシステム。LangGraphを活用し、複数の仮想ペルソナが並列で記事を評価します。

## 主な機能

- **多角的評価**: 技術専門家、ビジネスユーザー、一般読者、ドメイン専門家の視点で評価
- **非同期並列実行**: 最大4エージェント同時実行による高速処理
- **マルチLLM対応**: Gemini 2.5 Flash（デフォルト）、OpenAI、Claude をサポート
- **包括的レポート**: 評価結果と優先順位付き改善提案を生成
- **エラー耐性**: 自動リトライとフォールバック機構

## 前提条件

- Python 3.10以上
- LLMプロバイダーのAPIキー（以下のいずれか）
  - Google AI (Gemini)
  - OpenAI
  - Anthropic (Claude)

## インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd multi-agent-review-system

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 設定

`.env`ファイルを作成し、使用するLLMプロバイダーの設定を記述：

```bash
# LLMプロバイダー選択（gemini | openai | claude）
LLM_PROVIDER=gemini

# APIキー（使用するプロバイダーのもののみ必須）
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# オプション設定
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
MAX_CONCURRENT_AGENTS=4
LOG_LEVEL=INFO
```

## 使用方法

### 基本的な使用

```bash
# 記事ファイルを評価
python -m src.main evaluate path/to/article.md

# 標準入力から評価
echo "Your article content" | python -m src.main evaluate -

# 出力形式を指定（json | markdown）
python -m src.main evaluate article.md --output-format json
```

### 高度な使用

```bash
# 特定のペルソナのみで評価
python -m src.main evaluate article.md --personas tech_expert,general_reader

# タイムアウトを設定
python -m src.main evaluate article.md --timeout 120

# 詳細ログを出力
python -m src.main evaluate article.md --log-level DEBUG
```

## 出力例

```json
{
  "overall_score": 82.5,
  "evaluations": {
    "tech_expert": {
      "score": 85,
      "strengths": ["技術的に正確", "ベストプラクティスに準拠"],
      "weaknesses": ["エラーハンドリングが不十分"]
    },
    "business_user": {
      "score": 80,
      "strengths": ["実用的な内容", "ROIが明確"],
      "weaknesses": ["実装コストの言及なし"]
    }
  },
  "improvement_suggestions": [
    {
      "suggestion": "エラーハンドリングの例を追加",
      "priority": 0.8,
      "supported_by": ["tech_expert", "domain_expert"]
    }
  ]
}
```

## テスト

### テストの実行

```bash
# 全テスト実行
pytest

# カバレッジレポート生成
pytest --cov=src --cov-report=html

# 特定のテストのみ
pytest tests/unit  # 単体テストのみ
pytest -m "not integration"  # 統合テスト以外
```

## 開発

### コード品質チェック

```bash
# フォーマット
black src tests

# Lintチェック
flake8 src tests

# 型チェック
mypy src
```

### 開発用インストール

```bash
pip install -r requirements-dev.txt
pre-commit install
```

## プロジェクト構造

```
multi-agent-review-system/
├── src/
│   ├── agents/         # エージェント実装
│   ├── graph/          # LangGraphワークフロー
│   ├── utils/          # ユーティリティ
│   └── main.py         # エントリーポイント
├── tests/
│   ├── unit/           # 単体テスト
│   └── integration/    # 統合テスト
├── docs/               # ドキュメント
└── config/             # 設定ファイル
```

## 貢献

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 開発ガイドライン

- テストファーストで実装（TDD）
- チェックリストに従って開発
- コミットメッセージは明確に
- PRには必ずテストを含める

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 関連情報

- [要件定義書](docs/requirements-summary.md)
- [アーキテクチャ設計](docs/langgraph-agent-communication-design.md)
- [開発プロセス](docs/checklist-and-test-driven-development-process.md)
- [LangGraph公式ドキュメント](https://langchain-ai.github.io/langgraph/)

## 注意事項

- APIキーは絶対にコミットしないでください
- 大量の記事を評価する場合はAPI利用料金に注意してください
- 本番環境では適切なレート制限を設定してください

## サポート

問題や質問がある場合は、[Issues](https://github.com/yourusername/multi-agent-review-system/issues)で報告してください。

---
最終更新: 2025年1月