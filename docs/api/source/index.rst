Adoptive Market Crawler ドキュメント
================================

.. toctree::
   :maxdepth: 2
   :caption: 目次:

   modules/content_parser
   modules/gemini_analyzer
   modules/market_analyzer
   modules/neo4j_manager

概要
----

Adoptive Market Crawlerは、市場分析のための情報収集とナレッジ化システムです。
指定されたキーワードに関する市場分析に役立つ情報を収集し、Gemini-2.0を用いて解析し、
Neo4jデータベースにナレッジとして保存します。

主な機能
--------

* HTMLからの本文抽出と不要要素の除去（フォールバック戦略対応）
* Gemini-2.0を使用した市場影響度分析（リトライロジック実装）
* Neo4jへのナレッジ保存と時系列管理（トランザクション管理強化）
* 高度なエラーハンドリングとリカバリー機能
* パフォーマンスモニタリングとメトリクス収集

インデックス
-----------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 