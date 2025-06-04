# ドキュメント正確性検証ルール

## 📋 概要

AI支援開発におけるドキュメント記載の正確性を確保するための厳格な検証ルール。
事実に基づかない推測や憶測を排除し、客観的で検証可能な情報のみを記載する。

## 🎯 基本原則

### 1. 事実ベース記載の徹底
```markdown
# ❌ 推測による記載
pytest を実行してテストできます

# ✅ 事実確認後の記載
```bash
# 確認済みのMakeターゲット一覧
make up      # 開発環境起動（Makefile:35行目で確認）
make bash    # コンテナシェルアクセス（Makefile:16行目で確認）
make clean   # クリーンアップ（Makefile:55行目で確認）

# 注意: make test は現在未定義です（この例は意図的な悪い例）
```
```

### 2. 解釈と事実の明確な分離
```markdown
# ❌ 解釈を事実として記載
このプロジェクトは高性能です

# ✅ 事実に基づく解釈の記載
**パフォーマンス指標（実測値）**:
- レスポンスタイム: 12ms（pytest実行時間/テスト数で算出）
- テストカバレッジ: 91.77%（pytest --cov実行結果）

**解釈**: 上記データから、本プロジェクトは業界平均（50-70ms）を大幅に上回る高性能を示している
```

### 3. コマンド・ファイル存在の事前検証
```markdown
# 必須検証項目
1. コマンド実行確認: `command --help 2>&1 || echo "not found"`
2. ファイル存在確認: `ls -la path/to/file || echo "not found"`
3. 設定ファイル内容確認: 具体的な行番号・内容の明記
```

## 🔍 検証チェックリスト

### A. コマンド記載時の必須確認事項

#### A1. Make ターゲット
- [ ] `less Makefile` でMakefile直接確認（make helpは存在しない）
- [ ] 各ターゲットの動作確認
- [ ] 存在しないターゲットの明記

#### A2. Python スクリプト
- [ ] スクリプトファイルの存在確認
- [ ] `--help` オプションでの機能確認
- [ ] 実行時エラーハンドリングの確認

#### A3. システムコマンド
- [ ] `which command` での存在確認
- [ ] バージョン情報の取得・記載
- [ ] 依存関係の明確化

### B. 数値・統計情報の検証

#### B1. テストカバレッジ
```bash
# 検証方法
pytest --cov=app --cov-report=term | grep "TOTAL"
# 記載例: "91.77%（pytest --cov実行結果: 2024-12-XX時点）"
```

#### B2. パフォーマンス指標
```bash
# 検証方法
time python scripts/performance_test.py
# 記載例: "12ms（time コマンド実測値）"
```

#### B3. コード行数
```bash
# 検証方法
find app/ -name "*.py" -exec wc -l {} + | tail -1
# 記載例: "約1,200行（find + wc -l 実測値）"
```

## 🚨 禁止事項

### 1. 絶対に記載してはならない内容
- [ ] 未確認のコマンド・ファイルパス
- [ ] 推測による数値情報
- [ ] 憶測による機能説明
- [ ] 他プロジェクトからの類推情報

### 2. 条件付きで注意すべき内容
- [ ] 未来の実装予定（必ず「実装予定」を明記）
- [ ] 外部依存の機能（依存関係を明記）
- [ ] 環境依存の動作（動作確認環境を明記）

## 🔧 自動検証の実装

### 1. pre-commit フック
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 ドキュメント正確性チェック実行中..."

# 1. Makeターゲット検証
python scripts/verify_makefile_targets.py

# 2. ファイル参照検証
python scripts/verify_file_references.py

# 3. コマンド実行可能性検証
python scripts/verify_command_availability.py

if [ $? -ne 0 ]; then
    echo "❌ ドキュメント正確性チェックに失敗しました"
    exit 1
fi

echo "✅ ドキュメント正確性チェック完了"
```

### 2. GitHub Actions 統合
```yaml
name: Documentation Accuracy Check
on: [push, pull_request]
jobs:
  verify-docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Verify documentation accuracy
      run: |
        python scripts/verify_accuracy.py
        python scripts/verify_makefile_targets.py
```

## 📝 記載テンプレート

### 1. コマンド紹介テンプレート
```markdown
### コマンド名

**検証済み実行方法**:
```bash
# 実行コマンド（検証日: YYYY-MM-DD）
command --option value

# 期待される出力例
Expected output here...
```

**動作確認環境**:
- OS: Ubuntu 22.04
- Python: 3.10.12
- 検証日: 2024-12-XX
```

### 2. 数値情報テンプレート
```markdown
### 指標名

**実測値**: XX.XX%  
**測定方法**: `specific command here`  
**測定日時**: 2024-12-XX XX:XX  
**測定環境**: 環境詳細  

**解釈**: 実測値に基づく客観的な評価
```

### 3. 機能説明テンプレート
```markdown
### 機能名

**実装状況**: ✅完了 / 🚧開発中 / 📋計画中

**確認方法**:
```bash
# 動作確認コマンド
verification command here
```

**確認結果**: 実際の出力や動作内容

**備考**: 制限事項や注意点（事実ベース）
```

## 🔄 レビュープロセス

### 1. 自己チェック（必須）
- [ ] 記載内容を実際に実行・確認した
- [ ] 推測・憶測部分を「解釈」として明記した
- [ ] ソースコード・ログ等の根拠を明示した
- [ ] 確認不可能な内容は削除または修正した

### 2. ツール支援チェック（推奨）
```bash
# 実行前チェック
python scripts/verify_accuracy.py --target README.md

# コミット前チェック
git add . && git commit  # pre-commitフックが自動実行
```

### 3. 批判的レビュー（推奨）
- [ ] 第三者視点での内容確認
- [ ] 手順の再現可能性確認
- [ ] 不明瞭な表現の指摘・修正

## 📊 品質指標

### 目標値
- **命令実行成功率**: 100%（記載コマンドがすべて実行可能）
- **数値検証可能率**: 100%（記載数値がすべて検証可能）
- **ファイル参照正確率**: 100%（記載ファイルパスがすべて存在）

### 測定方法
```bash
# 月次品質レポート生成
python scripts/generate_accuracy_report.py --month 2024-12
```

## 🎓 教訓・改善点

### 過去の問題事例
1. **make test 記載事件（解決済み）**
   - 問題: 存在しないMakeターゲットを記載
   - 原因: Makefile確認不備
   - 対策: 事前確認の徹底

2. **性能数値根拠不明事件**
   - 問題: 測定根拠が不明な数値記載
   - 原因: 推測による記載
   - 対策: 測定方法・日時の必須記載

### 改善フィードバックループ
1. **週次レビュー**: ドキュメント正確性の確認
2. **月次改善**: 検証プロセスの最適化
3. **四半期見直し**: ルール・ツールの更新

---

**重要**: このルールは「正確性」を最優先とする。不明な内容は「調査中」「未確認」と素直に記載することで、読者への信頼性を向上させる。