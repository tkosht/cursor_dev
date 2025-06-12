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
        
    def get_migration_files(self) -> Dict[str, List[str]]:
        """移行対象ファイルをカテゴリ別に取得"""
        files = {
            "mandatory_rules": [
                "memory-bank/user_authorization_mandatory_rules.md",
                "memory-bank/testing_mandatory_rules.md",
                "memory-bank/code_quality_anti_hacking_rules.md",
                "memory-bank/documentation_accuracy_verification_rules.md"
            ],
            "core_knowledge": [
                "memory-bank/tdd_implementation_knowledge.md",
                "memory-bank/generic_tdd_patterns.md",
                "memory-bank/development_workflow_rules.md",
                "memory-bank/git_worktree_parallel_development_verified.md",
                "memory-bank/a2a_protocol_implementation_rules.md",
                "docs/02.basic_design/a2a_architecture.md",
                "docs/03.detail_design/a2a_implementation_guide.md",
                "docs/03.detail_design/a2a_tdd_implementation.md",
                "memory-bank/projectbrief.md",
                "memory-bank/critical_review_framework.md"
            ],
            "knowledge_patterns": [],
            "research_docs": [],
            "reference_docs": [],
            "templates": []
        }
        
        # memory-bank/knowledge/ 配下
        knowledge_dir = self.base_path / "memory-bank" / "knowledge"
        if knowledge_dir.exists():
            files["knowledge_patterns"] = [
                str(p.relative_to(self.base_path)) 
                for p in knowledge_dir.glob("*.md")
            ]
        
        # memory-bank/research/ 配下
        research_dir = self.base_path / "memory-bank" / "research"
        if research_dir.exists():
            files["research_docs"] = [
                str(p.relative_to(self.base_path)) 
                for p in research_dir.glob("*.md")
            ]
        
        # docs/90.references/ 配下
        ref_dir = self.base_path / "docs" / "90.references"
        if ref_dir.exists():
            files["reference_docs"] = [
                str(p.relative_to(self.base_path)) 
                for p in ref_dir.glob("*.md")
            ]
        
        # templates/ 配下
        templates_dir = self.base_path / "templates"
        if templates_dir.exists():
            files["templates"] = [
                str(p.relative_to(self.base_path)) 
                for p in templates_dir.glob("*.md")
            ]
        
        # その他のファイルを収集
        all_md_files = set()
        for pattern in ["memory-bank/**/*.md", "docs/**/*.md"]:
            all_md_files.update(
                str(p.relative_to(self.base_path)) 
                for p in self.base_path.glob(pattern)
            )
        
        # カテゴリ化されていないファイルを追加
        categorized_files = set()
        for category_files in files.values():
            categorized_files.update(category_files)
        
        files["other_docs"] = list(all_md_files - categorized_files)
        
        return files
    
    def validate_file_exists(self, file_path: str) -> bool:
        """ファイルの存在確認"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    async def migrate_file(self, file_path: str, category: str) -> Dict[str, Any]:
        """単一ファイルの移行（シミュレーション）"""
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
            
            # Cognee APIの呼び出しをシミュレート
            logger.info(f"Migrating {category}: {file_path}")
            # 実際の実装では：
            # await cognee.cognify(f"file:{self.base_path}/{file_path}")
            
            # レート制限対策
            await asyncio.sleep(0.5)
            
            result["status"] = "completed"
            self.migration_log.append(result)
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.error_log.append(result)
            logger.error(f"Failed to migrate {file_path}: {e}")
        
        return result
    
    async def migrate_category(self, category: str, files: List[str], 
                             batch_size: int = 10) -> Dict[str, Any]:
        """カテゴリ単位での移行"""
        logger.info(f"\n=== Migrating {category} ({len(files)} files) ===")
        
        results = {
            "category": category,
            "total": len(files),
            "success": 0,
            "failed": 0,
            "files": []
        }
        
        # バッチ処理
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.migrate_file(f, category) for f in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, dict):
                    results["files"].append(result)
                    if result["status"] == "completed":
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                else:
                    results["failed"] += 1
                    logger.error(f"Batch processing error: {result}")
            
            # バッチ間の待機
            if i + batch_size < len(files):
                logger.info(f"Batch {i//batch_size + 1} completed. Waiting...")
                await asyncio.sleep(2)
        
        return results
    
    async def run_migration(self) -> Dict[str, Any]:
        """移行処理のメイン実行"""
        start_time = time.time()
        
        logger.info("Starting Cognee migration...")
        
        # Phase 1: 初期セットアップ
        logger.info("\n=== Phase 1: Initial Setup ===")
        # 実際の実装では：
        # await cognee.prune()
        # await cognee.add_developer_rules(base_path=str(self.base_path))
        
        # ファイル収集
        files_by_category = self.get_migration_files()
        
        # 統計情報
        total_files = sum(len(files) for files in files_by_category.values())
        logger.info(f"Total files to migrate: {total_files}")
        
        migration_results = {
            "total_files": total_files,
            "categories": {},
            "start_time": start_time,
            "phases": []
        }
        
        # Phase 2: 必須ルール移行
        logger.info("\n=== Phase 2: Mandatory Rules ===")
        mandatory_results = await self.migrate_category(
            "mandatory_rules", 
            files_by_category["mandatory_rules"],
            batch_size=4
        )
        migration_results["categories"]["mandatory_rules"] = mandatory_results
        migration_results["phases"].append("mandatory_rules")
        
        # Phase 3: コア知識移行
        logger.info("\n=== Phase 3: Core Knowledge ===")
        core_results = await self.migrate_category(
            "core_knowledge",
            files_by_category["core_knowledge"],
            batch_size=5
        )
        migration_results["categories"]["core_knowledge"] = core_results
        migration_results["phases"].append("core_knowledge")
        
        # Phase 4: 補助知識移行
        logger.info("\n=== Phase 4: Auxiliary Knowledge ===")
        for category in ["knowledge_patterns", "research_docs", 
                        "reference_docs", "templates", "other_docs"]:
            if files_by_category[category]:
                results = await self.migrate_category(
                    category,
                    files_by_category[category],
                    batch_size=10
                )
                migration_results["categories"][category] = results
                migration_results["phases"].append(category)
        
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
    """メイン実行関数"""
    migration = CogneeMigration()
    
    # ドライラン（実際のCognee APIは呼ばない）
    logger.info("Running in DRY RUN mode (no actual Cognee API calls)")
    
    results = await migration.run_migration()
    
    # サマリー表示
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Total files: {results['total_files']}")
    print(f"Success: {results['success_count']}")
    print(f"Failed: {results['error_count']}")
    print(f"Duration: {results['duration']:.2f} seconds")
    print("\nBy Category:")
    for category, cat_results in results['categories'].items():
        print(f"  {category}: {cat_results['success']}/{cat_results['total']}")


if __name__ == "__main__":
    asyncio.run(main())