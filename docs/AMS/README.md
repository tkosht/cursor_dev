# Article Market Simulator (AMS) ドキュメント

## 概要

Article Market Simulatorは、記事やコンテンツに対する市場反応を高解像度な仮想ペルソナ群によるマルチエージェントシミュレーションを通じて予測・評価するシステムです。

## ドキュメント構成

本ドキュメントは以下の工程別に整理されています：

### 📋 01-requirements（要件定義）
- [AMS-REQ-001-system-requirements.md](01-requirements/AMS-REQ-001-system-requirements.md) - システム要件定義書
- [AMS-REQ-002-dynamic-architecture.md](01-requirements/AMS-REQ-002-dynamic-architecture.md) - 動的アーキテクチャ設計思想
- [AMS-REQ-003-langgraph-strategy.md](01-requirements/AMS-REQ-003-langgraph-strategy.md) - LangGraph使用戦略
- [AMS-REQ-004-initial-design.md](01-requirements/AMS-REQ-004-initial-design.md) - 初期システム設計書

### 📐 02-design（設計）

#### basic（基本設計）
- [AMS-BD-001-system-overview.md](02-design/basic/AMS-BD-001-system-overview.md) - システム基本設計書
- [AMS-BD-002-hierarchical-persona.md](02-design/basic/AMS-BD-002-hierarchical-persona.md) - 階層的ペルソナ生成システム設計
- [AMS-BD-003-simulation-framework.md](02-design/basic/AMS-BD-003-simulation-framework.md) - マルチエージェントシミュレーションフレームワーク設計
- [AMS-BD-004-visualization-data.md](02-design/basic/AMS-BD-004-visualization-data.md) - リアルタイム可視化データ構造設計

#### detailed（詳細設計）
※ 詳細設計は今後追加予定

### 🛠️ 03-implementation（実装）
- [AMS-IG-001-hierarchical-persona-integration.md](03-implementation/AMS-IG-001-hierarchical-persona-integration.md) - 階層的ペルソナ統合ガイド

## 命名規則

ドキュメントファイルは以下の命名規則に従います：

```
{システム}-{工程}-{番号}-{内容}.md
```

- **システム**: AMS（Article Market Simulator）
- **工程**: 
  - REQ（Requirements：要件定義）
  - BD（Basic Design：基本設計）
  - DD（Detailed Design：詳細設計）
  - IG（Implementation Guide：実装ガイド）
- **番号**: 3桁の連番（001, 002, ...）
- **内容**: ファイルの内容を表す簡潔な名称

## 読み進め方

1. **新規読者**: `01-requirements/AMS-REQ-001-system-requirements.md` から開始
2. **実装者**: `02-design/basic/AMS-BD-001-system-overview.md` から各設計書を確認
3. **開発者**: `03-implementation/` の実装ガイドを参照

## 更新履歴

- 2025-07-21: ドキュメント構造の整理と命名規則の統一化
- 2025-07-21: 基本設計ドキュメントの追加