# 正確性検証ルール

## 🎯 目的

ドキュメント、コード、コメントにおける情報の正確性を保証し、誤情報による混乱や信頼性低下を防止する。

## 🚨 基本原則

### 1. 真実性の原則
- **存在しないものを存在すると記載しない**
- **動作しないコマンドを動作すると記載しない**
- **未実装の機能を実装済みと記載しない**

### 2. 検証可能性の原則
- **すべての記述は実際に検証可能でなければならない**
- **コマンド例は実際に実行して確認する**
- **コード例はテストで動作を保証する**

### 3. 一貫性の原則
- **ドキュメント間で矛盾がないこと**
- **コードとドキュメントが一致すること**
- **コメントと実装が一致すること**

## 📋 検証プロセス

### 1. 自動検証（コミット前）

```python
#!/usr/bin/env python3
# scripts/verify_accuracy.py

import os
import re
import subprocess
import sys
from pathlib import Path

class AccuracyVerifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def verify_makefile_targets(self):
        """Makefileターゲットの検証"""
        print("🔍 Verifying Makefile targets...")
        
        # Makefileからターゲットを抽出
        makefile_targets = set()
        with open('Makefile', 'r') as f:
            for line in f:
                match = re.match(r'^([a-zA-Z0-9_-]+):', line)
                if match:
                    makefile_targets.add(match.group(1))
        
        # ドキュメントからmakeコマンドを抽出
        for doc_path in Path('.').glob('**/*.md'):
            with open(doc_path, 'r') as f:
                content = f.read()
                # make [target] パターンを検索
                make_commands = re.findall(r'make\s+([a-zA-Z0-9_-]+)', content)
                
                for cmd in make_commands:
                    if cmd not in makefile_targets:
                        self.errors.append(
                            f"{doc_path}: 'make {cmd}' は存在しないターゲットです"
                        )
    
    def verify_file_references(self):
        """ファイル参照の検証"""
        print("🔍 Verifying file references...")
        
        for doc_path in Path('.').glob('**/*.md'):
            with open(doc_path, 'r') as f:
                content = f.read()
                # ファイルパスパターンを検索
                file_refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for text, ref in file_refs:
                    if ref.startswith('http'):
                        continue  # URLはスキップ
                    if ref.startswith('#'):
                        continue  # アンカーリンクはスキップ
                    
                    # 相対パスを解決
                    ref_path = (doc_path.parent / ref).resolve()
                    if not ref_path.exists():
                        self.errors.append(
                            f"{doc_path}: リンク '{ref}' が存在しません"
                        )
    
    def verify_code_examples(self):
        """コード例の検証"""
        print("🔍 Verifying code examples...")
        
        for doc_path in Path('.').glob('**/*.md'):
            with open(doc_path, 'r') as f:
                content = f.read()
                
                # bashコードブロックを検索
                bash_blocks = re.findall(
                    r'```bash\n(.*?)\n```', 
                    content, 
                    re.DOTALL
                )
                
                for block in bash_blocks:
                    # 危険なコマンドはスキップ
                    if any(danger in block for danger in ['rm -rf', 'sudo']):
                        continue
                    
                    # ファイル操作コマンドの検証
                    file_commands = re.findall(
                        r'(?:cat|ls|cd|open)\s+([^\s|;&]+)', 
                        block
                    )
                    
                    for file_ref in file_commands:
                        if file_ref.startswith('$'):
                            continue  # 変数はスキップ
                        
                        # 特殊なパスは警告のみ
                        if file_ref in ['~', '.', '..', '/']:
                            continue
                        
                        if not Path(file_ref).exists():
                            self.warnings.append(
                                f"{doc_path}: コマンド内のパス '{file_ref}' が存在しない可能性"
                            )
    
    def verify_package_json_scripts(self):
        """package.jsonスクリプトの検証"""
        if Path('package.json').exists():
            print("🔍 Verifying package.json scripts...")
            import json
            
            with open('package.json', 'r') as f:
                package = json.load(f)
                scripts = package.get('scripts', {})
            
            for doc_path in Path('.').glob('**/*.md'):
                with open(doc_path, 'r') as f:
                    content = f.read()
                    npm_commands = re.findall(r'npm run\s+([a-zA-Z0-9_-]+)', content)
                    
                    for cmd in npm_commands:
                        if cmd not in scripts:
                            self.errors.append(
                                f"{doc_path}: 'npm run {cmd}' は存在しないスクリプトです"
                            )
    
    def verify_api_endpoints(self):
        """APIエンドポイントの検証"""
        print("🔍 Verifying API endpoints...")
        
        # FastAPIアプリからエンドポイントを抽出
        api_endpoints = set()
        for py_file in Path('app').glob('**/*.py'):
            with open(py_file, 'r') as f:
                content = f.read()
                # @app.get/@app.post パターンを検索
                endpoints = re.findall(
                    r'@app\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                    content
                )
                api_endpoints.update(endpoints)
        
        # ドキュメントからAPIエンドポイントを検証
        for doc_path in Path('.').glob('**/*.md'):
            with open(doc_path, 'r') as f:
                content = f.read()
                # GET /xxx, POST /xxx パターンを検索
                doc_endpoints = re.findall(
                    r'(?:GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]+)', 
                    content
                )
                
                for endpoint in doc_endpoints:
                    # パラメータを含むパスは簡易的にチェック
                    base_endpoint = re.sub(r'\{[^}]+\}', '*', endpoint)
                    if not any(api_ep == endpoint or 
                              re.match(base_endpoint.replace('*', '[^/]+'), api_ep) 
                              for api_ep in api_endpoints):
                        self.warnings.append(
                            f"{doc_path}: エンドポイント '{endpoint}' が見つかりません"
                        )
    
    def generate_report(self):
        """検証レポートの生成"""
        print("\n📊 Accuracy Verification Report")
        print("=" * 50)
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed!")
            return 0
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        return 1 if self.errors else 0
    
    def run(self):
        """全検証を実行"""
        self.verify_makefile_targets()
        self.verify_file_references()
        self.verify_code_examples()
        self.verify_package_json_scripts()
        self.verify_api_endpoints()
        return self.generate_report()

if __name__ == "__main__":
    verifier = AccuracyVerifier()
    sys.exit(verifier.run())
```

### 2. 手動検証チェックリスト

```yaml
manual_verification_checklist:
  documentation:
    - [ ] READMEのコマンドを実際に実行して確認
    - [ ] インストール手順を新環境で検証
    - [ ] APIドキュメントとコードの一致確認
    - [ ] 設定例が実際に動作することを確認
  
  code_comments:
    - [ ] コメントが実装と一致しているか
    - [ ] TODOコメントが最新か
    - [ ] 廃止されたコードへの参照がないか
  
  test_descriptions:
    - [ ] テストの説明が実際の動作と一致
    - [ ] モックの動作がドキュメントと一致
    - [ ] エラーケースの説明が正確か
```

### 3. CI/CDでの自動検証

```yaml
# .github/workflows/verify-accuracy.yml
name: Verify Documentation Accuracy

on:
  pull_request:
    paths:
      - '**.md'
      - 'Makefile'
      - 'package.json'
      - '.github/workflows/verify-accuracy.yml'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run accuracy verification
        run: |
          python scripts/verify_accuracy.py
      
      - name: Check broken links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          use-quiet-mode: 'yes'
          check-modified-files-only: 'yes'
```

## 🔧 修正ガイドライン

### 1. ドキュメント更新時

```markdown
<!-- 修正前 -->
## コマンド例
make test  # テストを実行

<!-- 修正後（Makefileを確認後） -->
## コマンド例
pytest --cov=app  # テストを実行（makeターゲットは未定義）
```

### 2. コード例の記載時

```python
# 悪い例：動作未確認のコード
def example():
    # このコードは動作します
    result = some_function()  # 実際には存在しない関数
    return result

# 良い例：動作確認済みのコード
def example():
    # app.utils.helperモジュールの関数を使用
    from app.utils.helper import some_function
    result = some_function()
    return result
```

### 3. 設定例の記載時

```yaml
# 悪い例：存在しない設定
config:
  feature_x: enabled  # この機能は未実装

# 良い例：実際の設定
config:
  # feature_x: enabled  # TODO: v2.0で実装予定
  feature_y: enabled  # 実装済み機能
```

## 📊 正確性メトリクス

### 測定項目

```python
class AccuracyMetrics:
    def calculate_accuracy_score(self):
        """ドキュメント正確性スコア（0-100）"""
        metrics = {
            'broken_links': self.count_broken_links(),
            'invalid_commands': self.count_invalid_commands(),
            'outdated_examples': self.count_outdated_examples(),
            'mismatched_comments': self.count_mismatched_comments(),
        }
        
        # スコア計算（問題が少ないほど高得点）
        total_issues = sum(metrics.values())
        total_items = self.count_total_verifiable_items()
        
        if total_items == 0:
            return 100
        
        accuracy_rate = (total_items - total_issues) / total_items
        return int(accuracy_rate * 100)
```

## 🚨 違反時の対応

### 重大度レベル

| レベル | 説明 | 対応 |
|--------|------|------|
| **Critical** | 存在しないコマンドの記載 | PR即却下、修正必須 |
| **High** | 動作しないコード例 | マージ前に修正必須 |
| **Medium** | 古い情報の残存 | 次回リリースまでに修正 |
| **Low** | 軽微な不整合 | バックログに追加 |

### エスカレーションプロセス

1. **自動検出時**：CI/CDでビルド失敗
2. **レビュー検出時**：修正依頼コメント
3. **本番検出時**：緊急修正パッチ

## 📝 予防策

### 1. ドキュメント生成の自動化

```python
# scripts/generate_command_docs.py
def generate_makefile_docs():
    """Makefileから自動的にドキュメント生成"""
    with open('Makefile', 'r') as f:
        targets = parse_makefile_targets(f.read())
    
    doc = "## 利用可能なMakeターゲット\n\n"
    for target, description in targets.items():
        doc += f"- `make {target}`: {description}\n"
    
    return doc
```

### 2. 変更時の自動通知

```yaml
# .github/workflows/notify-doc-update.yml
on:
  push:
    paths:
      - 'Makefile'
      - 'package.json'
      - 'app/**/routes.py'

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Create issue for doc update
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Documentation update required',
              body: 'Code changes detected. Please update related documentation.',
              labels: ['documentation', 'maintenance']
            })
```

## 🎯 継続的改善

### 定期レビュー

```yaml
scheduled_reviews:
  weekly:
    - command_examples_verification
    - broken_links_check
  
  monthly:
    - full_documentation_audit
    - code_comment_sync_check
  
  quarterly:
    - accuracy_metrics_review
    - process_improvement
```

### 改善提案プロセス

1. **問題の記録**：不正確な記述を発見したら即記録
2. **根本原因分析**：なぜ不正確な記述が生まれたか
3. **プロセス改善**：再発防止のためのルール追加
4. **効果測定**：改善後の正確性スコアを追跡

---

*このルールは、ドキュメントとコードの信頼性を保証するために継続的に更新されます。*