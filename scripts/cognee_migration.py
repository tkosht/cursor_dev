#!/usr/bin/env python3
"""
Cognee Knowledge Migration Script
プロジェクトの全ナレッジをCogneeに移行する
"""
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import logging
from dotenv import load_dotenv
import cognee

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CogneeMigration:
    """Cognee移行処理クラス"""
    
    def __init__(self, base_path: str = "/home/devuser/workspace"):
        self.base_path = Path(base_path)
        self.migration_log = []
        self.error_log = []
        
        # .env ファイルから環境変数を読み込み
        env_path = self.base_path / "dev-tools/external-repos/cognee/.env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Environment variables loaded from: {env_path}")
        else:
            logger.warning(f"Environment file not found: {env_path}")
        
    def get_migration_files(self) -> Dict[str, List[str]]:
        """移行対象ファイルをカテゴリ別に取得 - S+A級対応版"""
        files = {
            "s_grade_files": [
                # S級ファイル（全て登録済み）
                # "memory-bank/00-core/user_authorization_mandatory.md",     # ✅ 登録済み
                # "memory-bank/00-core/testing_mandatory.md",               # ✅ 登録済み  
                # "memory-bank/00-core/code_quality_anti_hacking.md",       # ✅ 登録済み
                # "memory-bank/01-cognee/mandatory_utilization_rules.md",   # ✅ 登録済み
                # "memory-bank/09-meta/progress_recording_mandatory_rules.md"  # ✅ 登録済み
            ],
            "a_grade_files": [
                # A級ファイル（残り5ファイル） - accuracy_verification_rules.md と critical_review_framework.md は実行中のため除外
                "memory-bank/02-organization/delegation_decision_framework.md",
                "memory-bank/02-organization/task_tool_delegation_integration.md",
                "memory-bank/04-quality/test_strategy.md",
                "memory-bank/04-quality/tdd_process_failures_lessons.md",
                "memory-bank/01-cognee/migration_procedure.md"
            ],
        }
        
        # S+A級のみの移行なので、他のカテゴリは除外
        
        return files
    
    def validate_file_exists(self, file_path: str) -> bool:
        """ファイルの存在確認"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def migrate_file(self, file_path: str, category: str) -> Dict[str, Any]:
        """単一ファイルの移行（Cognee Python API使用）"""
        result = {
            "file": file_path,
            "category": category,
            "status": "pending",
            "error": None,
            "timestamp": time.time()
        }
        
        try:
            if not self.validate_file_exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Cognee Python APIを使用
            logger.info(f"Migrating {category}: {file_path}")
            full_path = self.base_path / file_path
            
            # ファイル内容を読み込み
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cogneeにドキュメントを追加
            logger.info(f"Adding document to Cognee: {file_path}")
            await cognee.add(content, dataset_name="main_dataset")
            
            # cognifyはバッチごとに1回実行するので、ここでは実行しない
            result["status"] = "added"
            logger.info(f"Document added: {file_path}")
            
            self.migration_log.append(result)
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.error_log.append(result)
            logger.error(f"Failed to migrate {file_path}: {e}")
        
        return result
    
    
    async def migrate_category(self, category: str, files: List[str], 
                             batch_size: int = 3) -> Dict[str, Any]:
        """カテゴリ単位での移行（並列実行テスト）"""
        logger.info(f"\n=== Migrating {category} ({len(files)} files) ===")
        
        results = {
            "category": category,
            "total": len(files),
            "success": 0,
            "failed": 0,
            "files": []
        }
        
        # 並列実行テスト（バッチ処理）
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} files)")
            
            # バッチ内並列実行
            batch_results = await asyncio.gather(
                *[self.migrate_file(f, category) for f in batch],
                return_exceptions=True
            )
            
            for idx, result in enumerate(batch_results):
                if isinstance(result, dict):
                    results["files"].append(result)
                    if result["status"] in ["added", "completed"]:
                        results["success"] += 1
                        logger.info(f"✅ Completed: {batch[idx]}")
                    else:
                        results["failed"] += 1
                        logger.error(f"❌ Failed: {batch[idx]} - {result['error']}")
                else:
                    results["failed"] += 1
                    logger.error(f"❌ Exception in batch processing: {result}")
            
            # バッチ完了後にcognifyを実行
            logger.info(f"Running cognify for batch {i//batch_size + 1}...")
            try:
                await cognee.cognify()
                logger.info(f"Cognify completed for batch {i//batch_size + 1}")
                
                # 成功したファイルのステータスを更新
                for idx, file_result in enumerate(results["files"][-len(batch):]):
                    if file_result["status"] == "added":
                        file_result["status"] = "completed"
            except Exception as e:
                logger.error(f"Cognify failed for batch: {e}")
                # 失敗したファイルのステータスを更新
                for idx, file_result in enumerate(results["files"][-len(batch):]):
                    if file_result["status"] == "added":
                        file_result["status"] = "failed"
                        file_result["error"] = f"Cognify batch failed: {str(e)}"
            
            # バッチ間待機（メモリ負荷軽減）
            if i + batch_size < len(files):
                logger.info("Waiting 60 seconds before next batch...")
                await asyncio.sleep(60)
        
        return results
    
    async def run_migration(self) -> Dict[str, Any]:
        """S+A級移行処理のメイン実行（非同期版）"""
        start_time = time.time()
        
        logger.info("Starting S+A Grade Cognee migration...")
        
        # Cogneeの設定（環境変数から読み込み）
        cognee.config.llm_api_key = os.getenv("LLM_API_KEY")
        cognee.config.llm_model = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
        cognee.config.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        
        # データベース設定
        cognee.config.db_provider = os.getenv("DB_PROVIDER", "sqlite")
        cognee.config.graph_database_provider = os.getenv("GRAPH_DATABASE_PROVIDER", "networkx")
        cognee.config.vector_db_provider = os.getenv("VECTOR_DB_PROVIDER", "lancedb")
        
        logger.info("Cognee configured with environment settings")
        
        # ファイル収集
        files_by_category = self.get_migration_files()
        
        # 統計情報
        total_files = sum(len(files) for files in files_by_category.values())
        logger.info(f"Total S+A grade files to migrate: {total_files}")
        
        migration_results = {
            "total_files": total_files,
            "categories": {},
            "start_time": start_time,
            "phases": []
        }
        
        # Phase 2: S級ファイル移行
        logger.info("\n=== Phase 2: S-Grade Files ===")
        s_results = await self.migrate_category(
            "s_grade_files", 
            files_by_category["s_grade_files"],
            batch_size=1  # S級は慎重に1ファイルずつ（現在空なのでスキップ）
        )
        migration_results["categories"]["s_grade_files"] = s_results
        migration_results["phases"].append("s_grade_files")
        
        # Phase 3: A級ファイル移行  
        logger.info("\n=== Phase 3: A-Grade Files ===")
        a_results = await self.migrate_category(
            "a_grade_files",
            files_by_category["a_grade_files"],
            batch_size=2  # A級は2ファイルずつ（メモリ負荷考慮）
        )
        migration_results["categories"]["a_grade_files"] = a_results
        migration_results["phases"].append("a_grade_files")
        
        # 移行完了
        end_time = time.time()
        migration_results["end_time"] = end_time
        migration_results["duration"] = end_time - start_time
        migration_results["success_count"] = sum(
            cat["success"] for cat in migration_results["categories"].values()
        )
        migration_results["error_count"] = len(self.error_log)
        
        # 結果保存
        self.save_migration_report(migration_results)
        
        return migration_results
    
    def save_migration_report(self, results: Dict[str, Any]):
        """移行レポートの保存"""
        report_path = self.base_path / "output" / "reports" / "cognee_migration_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Migration report saved to: {report_path}")
        
        # エラーログの保存
        if self.error_log:
            error_path = self.base_path / "output" / "reports" / "cognee_migration_errors.json"
            with open(error_path, 'w', encoding='utf-8') as f:
                json.dump(self.error_log, f, indent=2, ensure_ascii=False)
            logger.warning(f"Error log saved to: {error_path}")


async def main():
    """メイン実行関数 - S+A級実行（非同期版）"""
    migration = CogneeMigration()
    
    logger.info("Running S+A Grade Migration with Cognee Python API")
    logger.info("Using batch processing with cognify after each batch...")
    
    results = await migration.run_migration()
    
    # サマリー表示
    print("\n" + "="*60)
    print("S+A GRADE MIGRATION SUMMARY")
    print("="*60)
    print(f"Total files: {results['total_files']}")
    print(f"Success: {results['success_count']}")
    print(f"Failed: {results['error_count']}")
    print(f"Duration: {results['duration']:.2f} seconds")
    print("\nBy Category:")
    for category, cat_results in results['categories'].items():
        print(f"  {category}: {cat_results['success']}/{cat_results['total']}")
    
    # 合格基準チェック
    success_rate = results['success_count'] / results['total_files'] * 100
    print(f"\n📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 100:
        print("✅ PASSED: All files migrated successfully!")
    elif success_rate >= 80:
        print("⚠️ PARTIAL: Most files migrated, check failed files")
    else:
        print("❌ FAILED: Migration did not meet success criteria")


if __name__ == "__main__":
    asyncio.run(main())