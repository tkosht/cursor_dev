# ユーザー承認必須ルール（構造化版）

## 🎯 **Rule ID**: AUTH-001 
## 📋 **Rule Name**: プロジェクト構造変更時のユーザー承認必須

---

## 🔴 **TRIGGER: 発動条件**

このルールは以下の**具体的な行動**を行う際に適用される：

### **主要トリガー**
1. **新規ディレクトリ作成**
   - `mkdir` コマンドの実行
   - IDE でのフォルダ作成
   - スクリプトによるディレクトリ自動生成

2. **既存構造の変更** 
   - ディレクトリの移動 (`mv` コマンド)
   - ディレクトリの削除 (`rm -rf` コマンド)
   - ディレクトリ名の変更

3. **構造定義の変更**
   - README.md のディレクトリ構造セクション変更
   - プロジェクト設定ファイルの構造変更

---

## 🎯 **SCOPE: 適用範囲**

### **✅ 対象に含まれる (INCLUDES)**
```yaml
directories:
  - プロジェクトルート配下のすべてのディレクトリ
  - サブディレクトリとその配下
  - シンボリックリンクで参照されるディレクトリ

changes:
  - README.md で定義された構造への影響
  - 他のチームメンバーの作業環境への影響
  - CI/CD パイプラインで使用されるパス

files:
  - 構造定義ファイル (README.md, .gitignore等)
  - プロジェクト設定ファイル (pyproject.toml等)
```

### **❌ 対象から除外される (EXCLUDES)**
```yaml
temporary_directories:
  - /tmp, /temp 配下
  - OS の一時ディレクトリ
  - プロセス固有の作業ディレクトリ

auto_generated:
  - __pycache__/ ディレクトリ
  - .git/ 配下の Git 内部ディレクトリ
  - node_modules/ 等のパッケージマネージャディレクトリ

build_artifacts:
  - output/ ディレクトリ
  - dist/, build/ ディレクトリ
  - coverage/ レポートディレクトリ

personal_workspace:
  - 個人用の開発環境設定
  - ローカルのみの設定ファイル
```

---

## ⚙️ **PREREQUISITES: 前提条件**

このルールが適用されるために必要な状況：

### **プロジェクト状態**
- [ ] プロジェクトがチーム開発環境である
- [ ] README.md でプロジェクト構造が定義されている
- [ ] Git リポジトリとして管理されている

### **影響範囲**
- [ ] 変更が他のメンバーの作業に影響する可能性がある
- [ ] 変更がビルド・テストプロセスに影響する可能性がある
- [ ] 変更がドキュメント・参照に影響する可能性がある

### **作業環境**
- [ ] 共有リポジトリでの作業
- [ ] マルチユーザー環境での開発

---

## 🚫 **EXCEPTIONS: 例外条件**

以下の場合はユーザー承認不要（ただし記録・報告は推奨）：

### **緊急時例外**
```yaml
emergency_conditions:
  - システム障害の緊急対応時
    action: 事後24時間以内に報告必須
  - セキュリティインシデント対応時  
    action: 事後48時間以内に詳細報告必須
  - データ損失回避のための緊急措置
    action: 実行前に可能な限り事前連絡
```

### **自動承認条件**
```yaml
auto_approved_patterns:
  - Git フック・CI/CD による自動生成
    condition: 既定のパターンに従う場合
  - 既存テンプレートに従った定型作業
    condition: テンプレートが事前承認済み
  - 一時的な検証・テスト用ディレクトリ
    condition: 24時間以内の自動削除設定
```

### **ロール別例外**
```yaml
project_owner:
  - 事前承認は不要
  - 事後報告を推奨（重要な変更時）
  
technical_lead:
  - 軽微な変更は事前承認不要
  - 重要な変更は事前連絡推奨
  
contributor:
  - すべての変更で事前承認必須
```

---

## ⚖️ **CRITERIA: 判定基準**

### **ユーザー承認の要件**
```yaml
permission_requirements:
  explicit_approval:
    - "承認" "OK" "Go ahead" 等の明示的意思表示
    - 理由の理解確認: "なぜこの変更が必要か理解した"
    - 影響の認識確認: "この変更による影響を理解した"
  
  understanding_verification:
    - 変更内容の具体的説明ができる
    - 影響範囲の認識を示せる  
    - 代替案の検討過程を理解している
```

### **客観的根拠の要件**
```yaml
evidence_requirements:
  necessity_proof:
    - 現状の問題点の定量的説明
    - 変更により解決される課題の明確化
    - 変更しない場合のリスク評価
  
  impact_analysis:
    - 影響を受けるファイル・機能のリスト
    - 他メンバーの作業への影響度評価
    - CI/CD・ビルドプロセスへの影響確認
  
  alternatives_consideration:
    - 代替案の検討結果
    - 各案のメリット・デメリット比較
    - 最適案選択の根拠
```

---

## 🔧 **ACTION: 実行手順**

### **Step 1: 事前確認**
```bash
# 自動チェックスクリプト実行
python scripts/check_structure_change.py

# 手動確認項目
- [ ] README.md の構造定義を確認
- [ ] 影響範囲を特定
- [ ] 代替案を検討
```

### **Step 2: 承認申請**
```markdown
**申請フォーマット**:

## 変更申請: [変更概要]

### 変更内容
- **作成/変更するディレクトリ**: [具体的パス]
- **変更の種類**: [新規作成/移動/削除/名前変更]

### 変更理由  
- **現状の問題**: [定量的説明]
- **解決される課題**: [具体的効果]
- **変更しない場合のリスク**: [リスク評価]

### 影響範囲
- **影響ファイル数**: [数値]
- **影響するメンバー**: [リスト]
- **CI/CDへの影響**: [有無と詳細]

### 代替案検討
1. **案A**: [内容とメリット・デメリット]
2. **案B**: [内容とメリット・デメリット]
3. **推奨案**: [選択理由]

### 実装予定
- **実装日時**: [予定]
- **実装方法**: [手順]
- **ロールバック手順**: [緊急時対応]
```

### **Step 3: 承認確認**
```markdown
承認確認項目:
- [ ] ユーザーから明示的な承認を得た
- [ ] 変更内容の理解を確認した
- [ ] 影響範囲の認識を確認した
- [ ] 実装タイミングを調整した
```

### **Step 4: 実装**
```bash
# 承認された内容に従って実装
# 変更ログの記録
echo "$(date): [AUTH-001] ${変更内容} - Approved by ${承認者}" >> structure_changes.log
```

### **Step 5: 完了報告**
```markdown
**完了報告フォーマット**:

## 変更完了報告: [変更概要]

### 実施内容
- **実施日時**: [実際の日時]
- **実施内容**: [実際に行った変更]
- **承認者**: [承認してくれた人]

### 結果
- **成功/失敗**: [結果]
- **予期しない影響**: [あれば記載]
- **後続作業**: [あれば記載]

### 確認事項
- [ ] CI/CD パイプラインが正常動作
- [ ] 他メンバーへの影響がない
- [ ] ドキュメントが更新済み
```

---

## 🔍 **Cognee での検索最適化**

この構造化により、以下のような具体的検索が可能になります：

### **適用判定の検索**
```python
# ❓ "新しいディレクトリを作りたいけど承認が必要？"
cognee.search("directory creation user authorization trigger conditions", "GRAPH_COMPLETION")
# ✅ 期待結果: "プロジェクトルート配下の新規ディレクトリ作成時は承認必要。ただし一時ディレクトリ、自動生成は除外"

# ❓ "緊急時でも承認が必要？"  
cognee.search("emergency exceptions user authorization", "GRAPH_COMPLETION")
# ✅ 期待結果: "システム障害・セキュリティインシデント時は事後報告で可。24-48時間以内"
```

### **具体的状況での判定**
```python
# ❓ "CI/CDで自動的にディレクトリができる場合は？"
cognee.search("automated directory creation CI/CD authorization exceptions", "GRAPH_COMPLETION")  
# ✅ 期待結果: "既定パターンに従うCI/CD自動生成は承認不要"

# ❓ "プロジェクトオーナーの場合の扱いは？"
cognee.search("project owner role authorization exceptions", "GRAPH_COMPLETION")
# ✅ 期待結果: "プロジェクトオーナーは事前承認不要、重要変更時は事後報告推奨"
```

---

## 📊 **改善効果の比較**

| 観点 | 構造化前 | 構造化後 |
|------|----------|----------|
| **適用判定** | 曖昧（解釈が分かれる） | 明確（客観的判定可能） |
| **例外処理** | 不明確 | 具体的条件と手順を明示 |
| **緊急時対応** | 指針なし | 明確な例外規定と事後手順 |
| **役割別扱い** | 言及なし | 役割別の明確な規定 |
| **Cognee検索** | 汎用的回答 | 状況特化の具体的回答 |

この構造化により、「承認が必要かどうか分からない」「例外的状況での判断に迷う」といった問題が解決され、適切なルール適用が可能になります。