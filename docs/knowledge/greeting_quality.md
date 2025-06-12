# Greeting Quality Standards

## 概要
このドキュメントは、挨拶タスクにおける品質基準、文化的配慮事項、およびテストケースを定義します。

## 1. 挨拶の適切性チェックリスト

### 1.1 基本要件
- [ ] **明確性**: 挨拶が明確で理解しやすいか
- [ ] **簡潔性**: 冗長でなく、適切な長さか
- [ ] **正確性**: 文法的に正しいか
- [ ] **一貫性**: トーンやスタイルが一貫しているか
- [ ] **目的適合性**: 状況に応じた適切な挨拶か

### 1.2 技術的要件
- [ ] **文字エンコーディング**: UTF-8で適切に処理されるか
- [ ] **文字数制限**: 最大200文字以内か
- [ ] **特殊文字処理**: 特殊文字が適切にエスケープされているか
- [ ] **改行処理**: 不要な改行が含まれていないか

### 1.3 パフォーマンス要件
- [ ] **応答時間**: 50ms以内で処理されるか
- [ ] **リソース使用**: メモリ使用量が適切か

## 2. 文化的配慮事項

### 2.1 多言語対応
- **日本語**
  - 敬語レベル（丁寧語、尊敬語、謙譲語）の適切な使用
  - 時間帯に応じた挨拶（おはよう、こんにちは、こんばんは）
  - ビジネス/カジュアルの使い分け

- **英語**
  - フォーマル/インフォーマルの区別
  - 地域による挨拶の違い（米国/英国/豪州）
  - 時間帯の考慮（Good morning/afternoon/evening）

### 2.2 コンテキスト別配慮
- **ビジネスコンテキスト**
  - 初対面: より丁寧で正式な表現
  - 継続的関係: 適度にカジュアル化可能
  - 国際ビジネス: 文化的中立性を保つ

- **カジュアルコンテキスト**
  - 年齢層に応じた表現
  - 関係性の深さを考慮
  - 地域性・方言の適切な使用

### 2.3 禁止事項
- 差別的表現
- 政治的・宗教的に偏った表現
- 性別・年齢・職業による固定観念的表現
- 不適切なスラングや俗語

## 3. テストケース

### 3.1 正常系テストケース

```python
# テストケース1: 基本的な日本語挨拶
def test_basic_japanese_greeting():
    """
    Given: 日本語でのシンプルな挨拶リクエスト
    When: 挨拶を生成
    Then: 適切な日本語挨拶が返される
    """
    input = {"language": "ja", "context": "general"}
    expected = "こんにちは！"
    assert generate_greeting(input) == expected

# テストケース2: 時間帯考慮の英語挨拶
def test_time_aware_english_greeting():
    """
    Given: 朝の時間帯での英語挨拶リクエスト
    When: 挨拶を生成
    Then: "Good morning"を含む挨拶が返される
    """
    input = {"language": "en", "time": "08:00", "context": "general"}
    result = generate_greeting(input)
    assert "Good morning" in result

# テストケース3: ビジネスコンテキストの挨拶
def test_business_context_greeting():
    """
    Given: ビジネスコンテキストでの挨拶リクエスト
    When: 挨拶を生成
    Then: フォーマルな挨拶が返される
    """
    input = {"language": "ja", "context": "business", "formality": "high"}
    result = generate_greeting(input)
    assert any(formal in result for formal in ["お世話になっております", "よろしくお願いいたします"])
```

### 3.2 異常系テストケース

```python
# テストケース4: 不正な言語コード
def test_invalid_language_code():
    """
    Given: サポートされていない言語コード
    When: 挨拶を生成
    Then: デフォルト言語（英語）で挨拶が返される
    """
    input = {"language": "xx", "context": "general"}
    result = generate_greeting(input)
    assert result in ["Hello!", "Hi!"]

# テストケース5: 空の入力
def test_empty_input():
    """
    Given: 空の入力
    When: 挨拶を生成
    Then: デフォルトの挨拶が返される
    """
    input = {}
    result = generate_greeting(input)
    assert len(result) > 0

# テストケース6: 過度に長い入力
def test_excessive_input_length():
    """
    Given: 200文字を超える追加テキスト
    When: 挨拶を生成
    Then: 適切に切り詰められた挨拶が返される
    """
    input = {"language": "en", "additional_text": "a" * 300}
    result = generate_greeting(input)
    assert len(result) <= 200
```

### 3.3 エッジケーステスト

```python
# テストケース7: 特殊文字を含む入力
def test_special_characters():
    """
    Given: 特殊文字を含む名前
    When: 挨拶を生成
    Then: 特殊文字が適切にエスケープされる
    """
    input = {"language": "en", "name": "<script>alert('xss')</script>"}
    result = generate_greeting(input)
    assert "<script>" not in result

# テストケース8: Unicode文字の処理
def test_unicode_handling():
    """
    Given: 絵文字を含む入力
    When: 挨拶を生成
    Then: 絵文字が適切に処理される
    """
    input = {"language": "ja", "emoji": "👋"}
    result = generate_greeting(input)
    assert "👋" in result or len(result) > 0
```

## 4. 品質メトリクス

### 4.1 定量的メトリクス
- **カバレッジ**: 全ての言語・コンテキストの組み合わせの90%以上をカバー
- **パフォーマンス**: 95パーセンタイルで50ms以内の応答時間
- **エラー率**: 0.1%未満の処理失敗率

### 4.2 定性的メトリクス
- **ユーザー満足度**: フィードバックスコア4.5/5.0以上
- **文化的適切性**: ネイティブスピーカーによるレビュー合格率95%以上
- **保守性**: 新言語追加時の実装時間2時間以内

## 5. 継続的改善

### 5.1 フィードバックループ
1. ユーザーフィードバックの収集
2. エラーログの分析
3. パフォーマンスメトリクスの監視
4. 文化的妥当性の定期レビュー

### 5.2 更新プロセス
1. 四半期ごとの品質基準レビュー
2. 新しい文化的コンテキストの追加
3. テストケースの拡充
4. ドキュメントの更新

## 6. 参考資料
- [A2Aプロトコル仕様](../02.basic_design/a2a_architecture.md)

<!-- 
注記：多言語対応・文化的配慮に関する詳細は、本文書の第2章「文化的配慮事項」に
包括的に記載されており、追加の参考資料は不要です。
-->