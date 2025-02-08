ContentParser モジュール
===================

.. automodule:: app.content_parser
   :members:
   :undoc-members:
   :show-inheritance:

概要
----

HTMLコンテンツを解析し、本文や関連情報を抽出するモジュールです。
フォールバック戦略を実装し、様々なHTML構造に対応可能です。

主な機能
--------

* HTMLからの本文抽出
* タイトルの抽出（複数の戦略）
* 日付情報の抽出
* URLの正規化
* エラー回復メカニズム 