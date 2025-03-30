# 設計原則ガイドライン

## 1. 基本方針

設計原則は以下の優先順位で適用します：

1. KISS（Keep It Simple, Stupid）
   - 最優先の原則
   - 複雑な実装より単純な実装を選択
   - 理解しやすさを重視

2. YAGNI（You Aren't Gonna Need It）
   - 現在必要ない機能は実装しない
   - 将来の拡張性より現在の要件を優先
   - オーバーエンジニアリングを避ける

3. DRY（Don't Repeat Yourself）
   - コードの重複は避ける
   - ただし、KISSを損なわない範囲で適用
   - 過度な抽象化は避ける

## 2. パラダイム選択の基準

### オブジェクト指向設計（優先的に適用）
以下の場合にOOPパターンを選択：
- ドメインモデルの表現が必要な場合
- 状態管理が重要な場合
- 継承による機能拡張が適切な場合

適用すべきSOLID原則：
1. 単一責任の原則（SRP）
   - 常に適用
   - クラスは一つの責任のみを持つ

2. オープン・クローズドの原則（OCP）
   - 拡張性が要求される場合に適用
   - 既存コードの修正なしで機能追加できるように

3. リスコフの置換原則（LSP）
   - 継承を使用する場合は必ず適用
   - 派生クラスは基底クラスと互換性を保つ

4. インターフェース分離の原則（ISP）
   - インターフェースを定義する場合に適用
   - 最小限のインターフェースに分割

5. 依存関係逆転の原則（DIP）
   - モジュール間の結合度を下げる必要がある場合に適用
   - 抽象に依存し、具象に依存しない

### 関数型設計（補完的に適用）
以下の場合に関数型パターンを選択：
- データ変換処理が中心の場合
- 副作用を最小限に抑えたい場合
- 並行処理が必要な場合

適用すべき原則：
1. 不変性（Immutability）
   - データの変更を最小限に
   - 副作用を避ける

2. 純粋関数（Pure Functions）
   - 入力が同じなら常に同じ出力
   - 外部状態に依存しない

3. 合成可能性（Composability）
   - 小さな関数を組み合わせて複雑な処理を実現
   - パイプライン処理の活用

## 3. 判断基準と適用例

### KISSの判断基準
- コードレビューで5分以内に理解できるか
- 特別なコメントなしで意図が伝わるか
- 初級プログラマーでも理解できるか

例：
```python
# Good (KISS)
def get_active_users(users):
    return [user for user in users if user.is_active]

# Avoid (過度に複雑)
def get_active_users(users):
    return list(filter(lambda user: user.status != 'inactive' 
                      and user.last_login is not None 
                      and (datetime.now() - user.last_login).days < 30, 
                      users))
```

### YAGNIの判断基準
- 現在の要件に明示されているか
- 実装コストに見合う確実な利用シーンがあるか
- 将来の利用可能性が80%以上あるか

例：
```python
# Good (YAGNI)
class UserService:
    def create_user(self, user_data):
        # 現在必要な処理のみを実装
        return User.create(user_data)

# Avoid (過度な将来対応)
class UserService:
    def create_user(self, user_data, role=None, permissions=None, 
                   notification_preferences=None, social_links=None):
        # 将来的に必要かもしれない機能まで実装
        pass
```

### DRYの判断基準
- 同じロジックが3回以上繰り返されているか
- 抽象化によってコードが理解しやすくなるか
- 保守性が向上するか

例：
```python
# Good (DRY)
def validate_input(value, min_length, max_length):
    if not min_length <= len(value) <= max_length:
        raise ValueError(f"Length must be between {min_length} and {max_length}")

# Avoid (過度なDRY)
def create_validator(*rules):
    def validate(value):
        return all(rule(value) for rule in rules)
    return validate
```

## 4. レビュー時のチェックリスト

### 基本原則
- [ ] KISSが守られているか
- [ ] 不要な機能が含まれていないか（YAGNI）
- [ ] 適切な範囲で重複が除去されているか（DRY）

### オブジェクト指向設計
- [ ] クラスの責任が明確か（SRP）
- [ ] 拡張のために修正が必要ないか（OCP）
- [ ] 継承が適切に使用されているか（LSP）
- [ ] インターフェースが適切に分割されているか（ISP）
- [ ] 依存関係が適切か（DIP）

### 関数型設計
- [ ] 不要な可変状態がないか
- [ ] 関数の副作用が最小限か
- [ ] 関数の合成が適切か

## 5. 例外事項

以下の場合は、原則の厳格な適用を緩和することができます：

1. パフォーマンス要件
   - 重要なパフォーマンス要件がある場合
   - ただし、必ずプロファイリングで効果を確認する

2. 外部システムとの統合
   - 外部システムの制約に従う必要がある場合
   - ただし、影響範囲を最小限に抑える

3. レガシーシステムとの互換性
   - 既存システムとの互換性が必要な場合
   - ただし、新規コードへの影響を防ぐ

## 6. 原則適用の記録

設計原則の適用判断は、以下の形式で記録します：

```markdown
## [YYYY-MM-DD] 設計判断: [タイトル]

### 状況
- 判断が必要となった背景
- 関連する要件や制約

### 検討した選択肢
1. 選択肢A
   - メリット
   - デメリット
2. 選択肢B
   - メリット
   - デメリット

### 決定
- 選択した方針
- 適用する原則
- 適用を緩和する原則（ある場合）

### 理由
- 決定の根拠
- 期待される効果
- 想定されるリスクと対策
```
```

この設計原則ガイドラインを project.mdc に反映し、既存の抽象的な記述を置き換えることを提案いたします。

認識済のルールファイル：
- global.mdc
- development.mdc
- project.mdc
- workflow.mdc
- rules.mdc 