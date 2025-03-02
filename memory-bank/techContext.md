# 技術コンテキスト

## 使用技術
- **言語**: Python 3.10
- **ベクトル検索**: FAISS
- **自然言語処理**: Sentence Transformers, OpenAI API
- **UI**: PyQt6
- **テスト**: pytest
- **ログ**: structlog
- **依存関係管理**: Poetry

## 開発環境
- **コンテナ化**: Docker
- **GPU対応**: CUDA 11.8
- **CI/CD**: GitHub Actions
- **コード品質**: flake8, black, isort

## 技術的制約
- メモリ使用量の最適化
- GPUリソースの効率的な管理
- 処理速度とレスポンス時間の確保
- APIレート制限への対応

## 依存関係
- **faiss-cpu/faiss-gpu**: ベクトル検索エンジン
- **sentence-transformers**: 埋め込みモデル
- **openai**: LLM API連携
- **tweepy**: Twitter API連携
- **PyQt6**: UIフレームワーク
- **structlog**: 構造化ロギング

## デプロイメント
- Dockerコンテナによる環境の一貫性確保
- CPU/GPU環境の両対応
- 環境変数による設定管理
- ボリュームマウントによるデータ永続化 