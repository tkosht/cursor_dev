# AMS テストレビュー アクションアイテム
## 次回セッション継続用チェックリスト

**前回セッション日**: 2025-08-10  
**レビュー完了文書**: [ams_test_review_critical_issues_report.md](./ams_test_review_critical_issues_report.md)  
**作業状態**: 要件違反の特定完了 → 修正実装待ち

---

## 🔴 Priority 1: 即座対応必須項目（1-2日以内）

### 1. モック削除と実API移行
- [ ] 全テストファイルのモック使用箇所をリストアップ
  - `tests/unit/test_aggregator.py` (line 79-83)
  - `tests/unit/test_reporter.py` (line 5)
  - `tests/integration/test_orchestrator_integration.py` (line 4)
- [ ] 実LLM API呼び出しに置換
- [ ] CI用の呼び出し回数制限実装（3-5回max）
- [ ] `.env.test` ファイルでテスト用API設定

### 2. 動的ペルソナ生成の実装
- [ ] 固定persona_typeの削除
  ```python
  # 削除対象
  persona_type="tech_enthusiast"  # ❌
  persona_type="general_reader"   # ❌
  ```
- [ ] `TargetAudienceAnalyzer` クラス実装
- [ ] `PersonaDesignOrchestrator` クラス実装
- [ ] 記事内容ベースの動的生成ロジック実装

### 3. テストの修正
- [ ] 動的ペルソナ生成のテストケース作成
- [ ] 実LLM統合テストの作成
- [ ] モック削除後の既存テスト修正

---

## 🟡 Priority 2: 重要改善項目（1週間以内）

### 4. ネットワークシミュレーション実装
- [ ] `NetworkEffectSimulator` クラス作成
- [ ] `GroupDynamicsSimulator` クラス作成
- [ ] ペルソナ間関係モデルの実装
- [ ] 時系列伝播アルゴリズムの実装
- [ ] 統合テストの作成

### 5. LangGraph高度機能
- [ ] StateGraphの条件付きルーティング実装
- [ ] Send APIによる並列ペルソナ生成
- [ ] Command APIのフロー制御
- [ ] テストケースの作成

### 6. パフォーマンステスト
- [ ] 50ペルソナ/10秒の生成速度テスト
- [ ] 50ペルソナ×10ステップ/60秒のシミュレーション速度テスト
- [ ] 並列処理の効率測定
- [ ] メモリ使用量の監視

---

## 🟢 Priority 3: 完成度向上（2週間以内）

### 7. E2Eテストシナリオ
- [ ] 記事入力→ペルソナ生成→シミュレーション→レポート出力
- [ ] 異なる記事タイプでの動作確認
- [ ] WebSocketストリーミングのテスト
- [ ] 可視化機能のテスト

### 8. ドキュメント更新
- [ ] 実装チェックリスト更新
- [ ] APIドキュメント作成
- [ ] アーキテクチャ図の更新
- [ ] テスト戦略ドキュメント更新

---

## 📁 関連ファイル一覧

### 修正が必要なファイル
```
app/ams/
├── src/agents/
│   ├── persona_generator.py         # 動的生成ロジック追加
│   ├── network_simulator.py         # 新規作成必要
│   └── orchestrator.py             # LangGraph高度機能追加
├── tests/
│   ├── unit/
│   │   ├── test_aggregator.py      # モック削除
│   │   ├── test_reporter.py        # モック削除
│   │   └── test_persona_generator.py # 動的生成テスト追加
│   ├── integration/
│   │   └── test_orchestrator_integration.py # 実API使用
│   └── performance/                # 新規作成必要
│       ├── test_generation_speed.py
│       └── test_simulation_performance.py
```

### 参照ドキュメント
```
docs/AMS/
├── 01-requirements/
│   └── AMS-REQ-001-system-requirements.md  # 要件定義（動的生成の仕様）
├── 03-implementation/
│   └── AMS-IG-001-implementation-checklist.md # 実装チェックリスト
└── ams_test_review_critical_issues_report.md  # 今回のレビュー結果
```

---

## 🚀 次回セッション開始手順

```bash
# 1. プロジェクトディレクトリへ移動
cd /home/devuser/workspace/app/ams

# 2. 作業状態の確認
cat docs/ams_test_review_action_items.md

# 3. 前回レビュー結果の確認
cat docs/ams_test_review_critical_issues_report.md

# 4. 現在のテスト実行（問題確認）
pytest tests/ -v

# 5. モック使用箇所の検索
grep -r "Mock\|patch" tests/

# 6. 作業開始
# Priority 1の項目から順次実施
```

---

## 📝 作業記録

| 日付 | 作業内容 | 完了項目 | 次回タスク |
|------|---------|---------|-----------|
| 2025-08-10 | テストレビュー実施 | 要件違反7件特定 | モック削除開始 |
| (次回) | - | - | - |

---

## ⚠️ 重要な注意事項

1. **モック使用は絶対禁止** - CLAUDE.mdの必須ルール違反
2. **動的生成が核心機能** - 固定役割では価値なし
3. **実API利用必須** - ただしCI環境では呼び出し数制限
4. **テストカバレッジの真実** - 現在20%、目標80%以上

---

**次回作業者へ**: このドキュメントの Priority 1 から着手してください。