# Difyホスト設定の柔軟化

## ステータス
- 決定日: 2024-03-10
- ステータス: 承認済み
- 実装: 完了

## コンテキスト
- Dify APIのエンドポイントが固定値として実装されていた
- カスタムホストの使用が必要なケースへの対応が必要
- 設定の柔軟性向上が求められていた

## 決定
- 環境変数 `DIFY_HOST` による設定をサポート
- デフォルト値として `https://api.dify.ai` を使用
- 完全なURLを指定可能に

## 結果
- カスタムホストの使用が可能に
- 既存の動作は維持（デフォルト値による後方互換性）
- テストカバレッジ95%を維持

## 実装詳細
1. 環境変数の追加
```python
self.dify_host = os.getenv("DIFY_HOST", "https://api.dify.ai")
```

2. APIエンドポイントの動的構築
```python
f"{self.dify_host}/v1/completion-messages"
```

3. テストケースの追加
- カスタムホスト設定のテスト
- 既存機能への影響がないことの確認

## 代替案
1. 設定ファイルによる管理
   - 理由: 環境変数の方が一般的で簡単
   - 結果: 不採用

2. URLの部分的な設定
   - 理由: 完全なURLの方が柔軟性が高い
   - 結果: 不採用

## 影響
### 正の影響
- 設定の柔軟性向上
- カスタム環境への対応が可能に
- 明確なデフォルト値の提供

### 負の影響
- なし（後方互換性を維持）

## 注意点
- 完全なURLを指定する必要あり
- HTTPSプロトコルの推奨
- 環境変数が未設定の場合はデフォルト値を使用

## 関連ドキュメント
- [techContext.md](../../memory-bank/techContext.md)
- [systemPatterns.md](../../memory-bank/systemPatterns.md)
- [activeContext.md](../../memory-bank/activeContext.md) 