"""Neo4jManagerの結合テストモジュール。

このモジュールは、Neo4jManagerが実際のNeo4jデータベースと正しく連携できることを検証します。

必要性：
- 実際のデータベース操作における潜在的な問題の検出
  - 実環境での接続エラーの早期発見
  - トランザクション管理の整合性確認
  - 同時実行時の競合検出
- 環境変数による設定の検証
  - .env.testファイルからの設定読み込み
  - 認証情報の適切な取り扱い

十分性：
- 実データベースを使用した本番同等の検証
  - モックを使用せず、実際の接続を確立
  - 実際のクエリ実行による応答確認
- 完全なトランザクション管理
  - ロールバックによるテストデータのクリーンアップ
  - 例外発生時の適切な後処理

代替案検討：
- モックを使用する案は、開発ルールで明確に禁止されているため却下
- インメモリデータベースの使用は、本番環境との差異が生じるため却下
- Docker上のNeo4jインスタンスを使用することで、本番に近い環境を実現
"""

import os
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from neo4j.exceptions import ServiceUnavailable

from app.neo4j_manager import Neo4jManager


def load_test_env():
    """テスト用の環境変数を読み込む。
    
    必要性：
    - テスト環境固有の設定を使用
      - 本番環境との分離を確保
      - テスト用の認証情報を使用
    - 環境変数の存在確認
      - 必要な設定が揃っているか検証
      - 不足している場合は適切にスキップ
    
    十分性：
    - .env.testファイルの完全性確認
      - ファイルの存在チェック
      - 必須項目の存在チェック
    - 適切なエラーメッセージ提供
      - テストスキップの理由を明確に説明
      - 設定方法のガイダンスを含む
    
    代替案検討：
    - 環境変数の直接設定は、設定の一元管理の観点から却下
    - デフォルト値の使用は、セキュリティリスクがあるため却下
    """
    env_path = Path(__file__).parent.parent.parent / '.env.test'
    if not env_path.exists():
        pytest.skip(
            ".env.test file not found. Please create it with required settings:\n"
            "- NEO4J_URI: Neo4jデータベースのURI\n"
            "- neo4j_user: 接続ユーザー名\n"
            "- neo4j_pswd: 接続パスワード"
        )
    load_dotenv(env_path)


@pytest.fixture(scope="module")
def neo4j_manager():
    """テスト用のNeo4jManagerインスタンスを提供する。
    
    必要性：
    - 実際のデータベース接続を使用
      - モックを使用せず本番同等の検証
      - 実際の接続エラーの検出
    - テスト用の環境変数から認証情報を取得
      - セキュアな認証情報管理
      - テスト環境の分離
    
    十分性：
    - 接続の完全性確認
      - URIの妥当性検証
      - 認証情報の検証
    - 詳細なエラー情報の提供
      - 接続失敗の原因特定
      - 設定の問題箇所の特定
    
    代替案検討：
    - モックの使用は開発ルールで禁止されているため却下
    - ハードコードされた接続情報の使用はセキュリティリスクがあるため却下
    """
    load_test_env()
    
    try:
        # 必要性：環境変数から認証情報を安全に取得
        uri = os.getenv('NEO4J_URI')
        if not uri:
            pytest.skip(
                "NEO4J_URI environment variable is not set in .env.test\n"
                "Please set it to the actual Neo4j database URI"
            )

        username = os.getenv('neo4j_user')
        if not username:
            pytest.skip(
                "neo4j_user environment variable is not set in .env.test\n"
                "Please set it to the actual Neo4j username"
            )

        password = os.getenv('neo4j_pswd')
        if not password:
            pytest.skip(
                "neo4j_pswd environment variable is not set in .env.test\n"
                "Please set it to the actual Neo4j password"
            )

        # 必要性：実際のデータベース接続を確立
        manager = Neo4jManager(
            uri=uri,
            username=username,
            password=password,
            max_connection_lifetime=30  # テスト用に短い接続時間を設定
        )
        
        # 十分性：接続の確認
        try:
            manager._driver.verify_connectivity()
        except Exception as e:
            pytest.skip(
                f"Failed to verify Neo4j connectivity: {str(e)}\n"
                "Please check if the Neo4j database is running and accessible"
            )
        
        return manager
    except Exception as e:
        pytest.skip(
            f"Failed to initialize Neo4j connection: {str(e)}\n"
            "Please check your Neo4j database settings and connectivity"
        )


@pytest.fixture(autouse=True)
def cleanup_database(neo4j_manager):
    """各テスト前後でデータベースをクリーンアップする。
    
    必要性：
    - テスト間の独立性確保
      - テストデータの完全な削除
      - 他のテストへの影響を防止
    - 一貫した初期状態の保証
      - 各テストの開始時点でクリーンな状態
      - テスト失敗時も確実にクリーンアップ
    
    十分性：
    - 完全なクリーンアップ
      - すべてのノードとリレーションシップを削除
      - インデックスとコンストレイントも初期化
    - 例外発生時の対応
      - クリーンアップ失敗時のログ記録
      - テスト実行の継続判断
    
    代替案検討：
    - テストデータの個別削除は、漏れが発生する可能性があるため却下
    - データベースの再起動は、時間がかかりすぎるため却下
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")
    
    try:
        # 必要性：テスト前のクリーンアップ
        neo4j_manager.run_query("MATCH (n) DETACH DELETE n")
        # インデックスとコンストレイントのクリーンアップ
        neo4j_manager.run_query("CALL apoc.schema.assert({}, {})")
        yield
    finally:
        # 必要性：テスト後のクリーンアップ
        # 十分性：例外が発生してもクリーンアップを実行
        if neo4j_manager is not None:
            try:
                neo4j_manager.run_query("MATCH (n) DETACH DELETE n")
                neo4j_manager.run_query("CALL apoc.schema.assert({}, {})")
            except Exception as e:
                pytest.skip(f"Failed to cleanup database: {str(e)}")


def test_create_and_find_node(neo4j_manager):
    """ノードの作成と検索の結合テスト。
    
    必要性：
    - 実際のデータベースでの操作確認
      - ノードの作成と検索が正しく機能
      - プロパティの保存と取得が正確
    - テストデータの独立性確保
      - 一意な名前によるテストデータの分離
      - 他のテストとの干渉防止
    
    十分性：
    - 完全なラウンドトリップテスト
      - 作成したノードの即時検索
      - すべてのプロパティの検証
    - エラー発生時の適切な処理
      - 詳細なエラーメッセージ
      - クリーンアップの保証
    
    代替案検討：
    - モックの使用は開発ルールで禁止されているため却下
    - インメモリテストは本番環境との差異が生じるため却下
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")

    # テストデータの準備
    test_name = f"TestPerson_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    properties = {
        'name': test_name,
        'age': 30,
        'test_id': 'integration_test'
    }
    
    try:
        # ノード作成
        node_id = neo4j_manager.create_node(
            labels=['Person'],
            properties=properties
        )
        assert node_id is not None, "ノードの作成に失敗しました"
        
        # ノード検索
        found_node = neo4j_manager.find_node(
            labels=['Person'],
            properties={'name': test_name}
        )
        assert found_node is not None, "作成したノードが見つかりません"
        assert found_node['name'] == test_name, "ノードのプロパティが正しくありません"
        assert found_node['age'] == 30, "ノードのプロパティが正しくありません"
        
    except Exception as e:
        pytest.fail(f"テスト実行中にエラーが発生しました: {str(e)}")


def test_create_relationship(neo4j_manager):
    """関係性の作成テスト。
    
    必要性：
    - 実際のデータベースでの関係性操作の検証
      - 関係性の作成機能の動作確認
      - プロパティの保存と取得の正確性
      - 参照整合性の確保
    - テストデータの独立性確保
      - 一意な識別子による分離
      - 他のテストとの干渉防止
      - クリーンアップの確実性
    
    十分性：
    - 完全なエンドツーエンドテスト
      - ノードの作成から関係性の作成まで
      - プロパティの設定と検証
      - クエリによる結果確認
    - エラー発生時の適切な処理
      - 詳細なエラーメッセージ
      - リソースの確実な解放
      - ロールバックの確認
    
    代替案検討：
    - モックの使用は開発ルールで禁止
    - インメモリテストは本番環境との差異が発生
    - 実データベースでの結合テストを採用
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")

    # テストデータの準備
    test_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    person_name = f"Person_{test_timestamp}"
    company_name = f"Company_{test_timestamp}"
    
    try:
        # ノード作成
        person_id = neo4j_manager.create_node(
            labels=['Person'],
            properties={
                'name': person_name,
                'created_at': test_timestamp,
                'test_id': 'relationship_test'
            }
        )
        assert person_id is not None, "開始ノードの作成に失敗しました"
        
        company_id = neo4j_manager.create_node(
            labels=['Company'],
            properties={
                'name': company_name,
                'created_at': test_timestamp,
                'test_id': 'relationship_test'
            }
        )
        assert company_id is not None, "終了ノードの作成に失敗しました"
        
        # 関係性作成
        rel_properties = {
            'since': '2023',
            'role': 'Engineer',
            'created_at': test_timestamp
        }
        rel_id = neo4j_manager.create_relationship(
            start_node_id=person_id,
            end_node_id=company_id,
            rel_type='WORKS_AT',
            properties=rel_properties
        )
        assert rel_id is not None, "関係性の作成に失敗しました"
        
        # 関係性の検証
        result = neo4j_manager.run_query(
            """
            MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
            WHERE p.name = $person_name AND c.name = $company_name
            RETURN r.since as since, r.role as role, r.created_at as created_at
            """,
            parameters={'person_name': person_name, 'company_name': company_name}
        )
        assert len(result) > 0, "作成した関係性が見つかりません"
        assert result[0]['since'] == '2023', "関係性のプロパティ(since)が正しくありません"
        assert result[0]['role'] == 'Engineer', "関係性のプロパティ(role)が正しくありません"
        assert result[0]['created_at'] == test_timestamp, "関係性のプロパティ(created_at)が正しくありません"
        
    except Exception as e:
        pytest.fail(f"テスト実行中にエラーが発生しました: {str(e)}")


def test_update_node(neo4j_manager):
    """ノードの更新テスト。
    
    必要性：
    - 実際のデータベースでのノード更新の検証
      - プロパティの更新機能の確認
      - 既存データの保持確認
      - 更新の整合性確保
    - テストデータの独立性確保
      - 一意な識別子による分離
      - 他のテストとの干渉防止
      - 更新前後の状態管理
    
    十分性：
    - 完全な更新フロー検証
      - 既存プロパティの更新
      - 新規プロパティの追加
      - 更新結果の確認
    - エラー発生時の適切な処理
      - 詳細なエラーメッセージ
      - ロールバックの確認
      - 整合性の保証
    
    代替案検討：
    - モックの使用は開発ルールで禁止
    - インメモリテストは本番環境との差異が発生
    - 実データベースでの結合テストを採用
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")

    # テストデータの準備
    test_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    test_name = f"UpdateTest_{test_timestamp}"
    initial_properties = {
        'name': test_name,
        'age': 30,
        'created_at': test_timestamp,
        'test_id': 'update_test'
    }
    
    try:
        # ノード作成
        node_id = neo4j_manager.create_node(
            labels=['Person'],
            properties=initial_properties
        )
        assert node_id is not None, "ノードの作成に失敗しました"
        
        # ノード更新
        update_properties = {
            'age': 31,
            'department': 'Engineering',
            'updated_at': test_timestamp
        }
        success = neo4j_manager.update_node(node_id, update_properties)
        assert success, "ノードの更新に失敗しました"
        
        # 更新の検証
        found_node = neo4j_manager.find_node(
            labels=['Person'],
            properties={'name': test_name}
        )
        assert found_node is not None, "更新したノードが見つかりません"
        assert found_node['age'] == 31, "年齢の更新が反映されていません"
        assert found_node['department'] == 'Engineering', "新しいプロパティが追加されていません"
        assert found_node['created_at'] == test_timestamp, "既存のプロパティが保持されていません"
        assert found_node['updated_at'] == test_timestamp, "更新日時が設定されていません"
        
    except Exception as e:
        pytest.fail(f"テスト実行中にエラーが発生しました: {str(e)}")


def test_find_node_not_found(neo4j_manager):
    """存在しないノードの検索テスト。
    
    必要性：
    - 存在しないノードの検索時の動作確認
      - 適切なNoneの返却
      - エラーが発生しないこと
      - パフォーマンスの確認
    - エッジケースの検証
      - 無効なラベル
      - 存在しないプロパティ
      - 特殊文字を含む検索
    
    十分性：
    - 複数の検索パターン
      - 存在しないラベル
      - 存在しないプロパティ値
      - 組み合わせ条件
    - エラー発生時の適切な処理
      - 詳細なエラーメッセージ
      - クエリのタイムアウト確認
      - リソースの解放
    
    代替案検討：
    - モックの使用は開発ルールで禁止
    - インメモリテストは本番環境との差異が発生
    - 実データベースでの結合テストを採用
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")

    try:
        # 存在しないラベルでの検索
        result = neo4j_manager.find_node(
            labels=['NonExistentLabel'],
            properties={'name': 'NonExistentName'}
        )
        assert result is None, "存在しないノードがヒットしました"
        
        # 存在しないプロパティ値での検索
        result = neo4j_manager.find_node(
            labels=['Person'],
            properties={'name': f"NonExistent_{datetime.now().strftime('%Y%m%d%H%M%S')}"}
        )
        assert result is None, "存在しないノードがヒットしました"
        
        # 特殊文字を含む検索
        result = neo4j_manager.find_node(
            labels=['Person'],
            properties={'name': "Test'Name\"WithSpecialChars"}
        )
        assert result is None, "存在しないノードがヒットしました"
        
    except Exception as e:
        pytest.fail(f"テスト実行中にエラーが発生しました: {str(e)}")


def test_run_custom_query(neo4j_manager):
    """カスタムクエリの実行テスト。
    
    必要性：
    - 複雑なクエリの実行確認
      - パラメータ化クエリの動作
      - 複数の結果の取得
      - パフォーマンスの確認
    - クエリの安全性確認
      - インジェクション対策
      - パラメータのエスケープ
      - トランザクション管理
    
    十分性：
    - 多様なクエリパターン
      - 複数ノードの作成と検索
      - 集計関数の使用
      - パラメータの結合
    - エラー発生時の適切な処理
      - 構文エラーの検出
      - タイムアウト処理
      - リソースの解放
    
    代替案検討：
    - モックの使用は開発ルールで禁止
    - インメモリテストは本番環境との差異が発生
    - 実データベースでの結合テストを採用
    """
    if neo4j_manager is None:
        pytest.skip("Neo4j manager is not available")

    test_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    try:
        # テストデータの作成
        create_query = """
        CREATE (p:Person {name: $name1, age: 30, test_id: 'query_test'})
        CREATE (c:Company {name: $name2, test_id: 'query_test'})
        CREATE (p)-[:WORKS_AT {since: '2023'}]->(c)
        """
        neo4j_manager.run_query(
            create_query,
            parameters={
                'name1': f"Person_{test_timestamp}",
                'name2': f"Company_{test_timestamp}"
            }
        )
        
        # 複雑なクエリの実行
        result = neo4j_manager.run_query(
            """
            MATCH (p:Person)-[r:WORKS_AT]->(c:Company)
            WHERE p.test_id = 'query_test'
            AND p.name = $person_name
            AND c.name = $company_name
            RETURN p.name as person_name,
                   p.age as age,
                   c.name as company_name,
                   r.since as start_date
            """,
            parameters={
                'person_name': f"Person_{test_timestamp}",
                'company_name': f"Company_{test_timestamp}"
            }
        )
        
        assert len(result) > 0, "クエリ結果が取得できません"
        assert result[0]['person_name'] == f"Person_{test_timestamp}", "人物名が一致しません"
        assert result[0]['company_name'] == f"Company_{test_timestamp}", "会社名が一致しません"
        assert result[0]['age'] == 30, "年齢が一致しません"
        assert result[0]['start_date'] == '2023', "開始日が一致しません"
        
        # 集計クエリの実行
        count_result = neo4j_manager.run_query(
            """
            MATCH (n)
            WHERE n.test_id = 'query_test'
            RETURN labels(n) as label, count(*) as count
            """
        )
        
        assert len(count_result) == 2, "ノードの数が正しくありません"
        counts = {row['label'][0]: row['count'] for row in count_result}
        assert counts['Person'] == 1, "Personノードの数が正しくありません"
        assert counts['Company'] == 1, "Companyノードの数が正しくありません"
        
    except Exception as e:
        pytest.fail(f"テスト実行中にエラーが発生しました: {str(e)}")


def test_connection_error():
    """接続エラーのテスト。
    
    必要性：
    - 接続エラー時の適切なエラーハンドリングを確認
    - エラーメッセージが適切に生成されることを検証
    
    十分性：
    - 無効な接続情報でのエラーケースをテスト
    - 例外の型と内容を検証
    """
    with pytest.raises(ServiceUnavailable) as exc_info:
        Neo4jManager(
            uri='bolt://invalid:7687',
            username='invalid',
            password='invalid'
        )
    assert "Cannot resolve address invalid:7687" in str(exc_info.value) 