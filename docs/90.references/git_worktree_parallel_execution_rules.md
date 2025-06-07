# Git Worktree並列実行方式 正式ルール

**文書種別**: 技術仕様書  
**バージョン**: 1.0.0  
**制定日**: 2025-06-07  
**適用対象**: Claude CLI並列実行環境  
**ステータス**: 正式採用

## 📋 目次

1. [概要](#概要)
2. [基本原則](#基本原則)
3. [環境構築ルール](#環境構築ルール)
4. [実行ルール](#実行ルール)
5. [安全プロトコル](#安全プロトコル)
6. [品質保証ルール](#品質保証ルール)
7. [監視・検証ルール](#監視検証ルール)
8. [クリーンアップルール](#クリーンアップルール)
9. [実践テンプレート](#実践テンプレート)
10. [トラブルシューティング](#トラブルシューティング)

## 概要

### 目的
Claude CLIを使用した並列タスク実行において、ファイル競合を完全に排除し、安全かつ効率的な開発環境を提供する。

### 解決する課題
- **ファイル競合**: 複数のClaude CLIプロセスによる同一ファイルへの同時書き込み
- **データ破損**: 競合状態によるファイル内容の不整合
- **品質劣化**: 並列実行による品質チェックの漏れ

### 採用理由
Git worktreeによる物理的分離は以下の利点を提供：
- **完全な競合回避**: 各タスクが独立したファイルシステム上で動作
- **Git統合**: ブランチ管理と自然に統合
- **ロールバック容易性**: 問題発生時の復旧が簡単

## 基本原則

### 1. 物理的分離の原則
```
各並列タスクは必ず独立したworktreeで実行する
```

### 2. 明示的管理の原則
```
すべてのworktreeは明示的に作成・削除し、放置しない
```

### 3. 品質維持の原則
```
並列実行でも単一実行と同等の品質基準を維持する
```

### 4. トレーサビリティの原則
```
各タスクの実行履歴と結果を追跡可能にする
```

## 環境構築ルール

### Rule 1: Worktreeディレクトリ構造

```bash
project_root/
├── worker/                 # Worktree専用ディレクトリ（必須）
│   ├── task_001/          # タスク別worktree
│   ├── task_002/
│   └── task_003/
├── logs/                  # 実行ログディレクトリ
│   ├── task_001.log
│   ├── task_002.log
│   └── task_003.log
└── .gitignore             # worker/を無視設定に追加
```

**必須設定**:
```bash
# .gitignoreに追加
worker/
logs/
```

### Rule 2: Worktree作成標準

```bash
# 標準作成コマンド
git worktree add worker/${TASK_ID} -b ${BRANCH_NAME}

# 命名規則
# TASK_ID: task_NNN (3桁ゼロパディング)
# BRANCH_NAME: feature/${component}-${functionality}
```

**例**:
```bash
git worktree add worker/task_001 -b feature/auth-login
git worktree add worker/task_002 -b feature/auth-logout
git worktree add worker/task_003 -b feature/auth-session
```

### Rule 3: 環境検証

worktree作成後、必ず以下を実行：

```bash
# 作成確認
git worktree list | grep worker/${TASK_ID}

# ブランチ確認
cd worker/${TASK_ID} && git branch --show-current

# 依存関係セットアップ
cd worker/${TASK_ID} && poetry install
```

## 実行ルール

### Rule 4: タスク分解基準

並列実行可能なタスクの条件：

1. **独立性**: 他タスクの結果に依存しない
2. **ファイル分離**: 異なるファイル・ディレクトリを対象
3. **適切な粒度**: 5分〜30分で完了する規模
4. **明確な成果物**: 完了条件が明確

### Rule 5: 実行パターン

#### パターンA: シンプル並列実行
```bash
# 各worktreeで独立実行
for task_id in 001 002 003; do
    (
        cd worker/task_${task_id}
        claude -p "タスク${task_id}を実装" > ../../logs/task_${task_id}.log 2>&1
    ) &
done
wait
```

#### パターンB: 段階的並列実行
```bash
# Phase 1: 分析タスク（読み取り専用）
for task_id in 001 002 003; do
    (
        cd worker/task_${task_id}
        claude -p "モジュール${task_id}の分析" > analysis_${task_id}.md
    ) &
done
wait

# Phase 2: 実装タスク
for task_id in 001 002 003; do
    (
        cd worker/task_${task_id}
        claude -p "analysis_${task_id}.mdを基に実装"
    ) &
done
wait
```

### Rule 6: 並列度制限

```bash
# 最大並列数の計算
MAX_PARALLEL=$(nproc)  # CPU数
RECOMMENDED_PARALLEL=$((MAX_PARALLEL / 2))  # 推奨値

# セマフォによる制限実装
parallel_execute() {
    local max_jobs=${1:-$RECOMMENDED_PARALLEL}
    local job_count=0
    
    for task in "${tasks[@]}"; do
        while [ $(jobs -r | wc -l) -ge $max_jobs ]; do
            sleep 1
        done
        execute_task "$task" &
    done
    wait
}
```

## 安全プロトコル

### Rule 7: 事前競合チェック

実行前に必ず競合可能性を検証：

```bash
#!/bin/bash
# check_conflicts.sh

check_file_conflicts() {
    local tasks=("$@")
    local all_files=()
    
    for task_id in "${tasks[@]}"; do
        # 各タスクで変更予定のファイルを収集
        cd worker/task_${task_id}
        git diff --name-only >> /tmp/files_${task_id}.txt
        all_files+=($(<"/tmp/files_${task_id}.txt"))
    done
    
    # 重複チェック
    if [ $(printf '%s\n' "${all_files[@]}" | sort | uniq -d | wc -l) -gt 0 ]; then
        echo "ERROR: ファイル競合の可能性があります"
        printf '%s\n' "${all_files[@]}" | sort | uniq -d
        return 1
    fi
    
    echo "✅ 競合チェック: 問題なし"
    return 0
}
```

### Rule 8: 実行時監視

```bash
# 実行状況のリアルタイム監視
monitor_parallel_execution() {
    while true; do
        clear
        echo "=== Worktree並列実行状況 ==="
        echo "時刻: $(date)"
        echo ""
        
        # 各worktreeの状態表示
        for worktree in worker/task_*; do
            if [ -d "$worktree" ]; then
                task_id=$(basename $worktree)
                branch=$(cd $worktree && git branch --show-current)
                changes=$(cd $worktree && git status --porcelain | wc -l)
                echo "[$task_id] ブランチ: $branch, 変更数: $changes"
            fi
        done
        
        echo ""
        echo "実行中のプロセス:"
        ps aux | grep claude | grep -v grep
        
        sleep 5
    done
}
```

### Rule 9: エラーハンドリング

```bash
# エラー時の自動ロールバック
execute_with_rollback() {
    local task_id=$1
    local worktree="worker/task_${task_id}"
    
    # 実行前の状態を記録
    cd $worktree
    local initial_commit=$(git rev-parse HEAD)
    
    # タスク実行
    if ! claude -p "タスクを実装"; then
        echo "ERROR: タスク${task_id}が失敗しました"
        
        # ロールバック
        git reset --hard $initial_commit
        git clean -fd
        
        # エラーログ記録
        echo "[$(date)] Task ${task_id} failed and rolled back" >> ../../logs/errors.log
        return 1
    fi
    
    return 0
}
```

## 品質保証ルール

### Rule 10: 個別品質チェック

各worktreeで独立して品質チェックを実行：

```bash
# quality_check_parallel.sh
run_quality_checks() {
    local task_id=$1
    local worktree="worker/task_${task_id}"
    
    cd $worktree
    
    # 品質チェック実行
    echo "=== Task ${task_id} 品質チェック ==="
    
    # 1. テスト実行
    if ! pytest --cov=app --cov-fail-under=85; then
        echo "❌ テスト失敗: Task ${task_id}"
        return 1
    fi
    
    # 2. コード品質
    if ! flake8 app/ tests/ --max-complexity=10; then
        echo "❌ Flake8違反: Task ${task_id}"
        return 1
    fi
    
    # 3. フォーマット
    black app/ tests/ --check
    isort app/ tests/ --check-only
    
    echo "✅ 品質チェック合格: Task ${task_id}"
    return 0
}

# 並列品質チェック
for task_id in 001 002 003; do
    run_quality_checks $task_id &
done
wait
```

### Rule 11: 統合前検証

マージ前の必須チェック：

```bash
pre_merge_validation() {
    local branch=$1
    
    # 1. コンフリクトチェック
    if ! git merge --no-commit --no-ff $branch; then
        echo "❌ マージコンフリクトあり"
        git merge --abort
        return 1
    fi
    git merge --abort
    
    # 2. 統合テスト準備
    git merge $branch
    
    # 3. 全体品質チェック
    python scripts/quality_gate_check.py
    
    return $?
}
```

## 監視・検証ルール

### Rule 12: 実行ログ管理

```bash
# ログ構造
logs/
├── execution/           # 実行ログ
│   ├── task_001_20250607_120000.log
│   └── task_002_20250607_120100.log
├── quality/            # 品質チェックログ
│   ├── task_001_quality.log
│   └── task_002_quality.log
└── summary/            # サマリーレポート
    └── parallel_execution_20250607.md
```

### Rule 13: メトリクス収集

```python
# metrics_collector.py
import json
import time
from pathlib import Path
from datetime import datetime

class ParallelExecutionMetrics:
    def __init__(self):
        self.metrics_file = Path("logs/metrics/execution_metrics.json")
        self.metrics = []
    
    def record_task_start(self, task_id: str, worktree: str):
        self.metrics.append({
            "task_id": task_id,
            "worktree": worktree,
            "start_time": datetime.now().isoformat(),
            "status": "started"
        })
        self._save()
    
    def record_task_complete(self, task_id: str, success: bool, duration: float):
        for metric in self.metrics:
            if metric["task_id"] == task_id:
                metric["end_time"] = datetime.now().isoformat()
                metric["status"] = "success" if success else "failed"
                metric["duration_seconds"] = duration
                break
        self._save()
    
    def generate_report(self):
        total_tasks = len(self.metrics)
        successful = sum(1 for m in self.metrics if m["status"] == "success")
        failed = sum(1 for m in self.metrics if m["status"] == "failed")
        
        return {
            "total_tasks": total_tasks,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_tasks if total_tasks > 0 else 0,
            "average_duration": self._calculate_average_duration()
        }
```

### Rule 14: 定期的な状態確認

```bash
# health_check.sh
#!/bin/bash

check_worktree_health() {
    echo "=== Worktree Health Check ==="
    echo "実行時刻: $(date)"
    
    # 1. Worktree一覧
    echo -e "\n[Worktree状態]"
    git worktree list
    
    # 2. ディスク使用量
    echo -e "\n[ディスク使用量]"
    du -sh worker/*
    
    # 3. 未コミット変更
    echo -e "\n[未コミット変更]"
    for worktree in worker/task_*; do
        if [ -d "$worktree" ]; then
            echo -n "$(basename $worktree): "
            (cd $worktree && git status --porcelain | wc -l) || echo "エラー"
        fi
    done
    
    # 4. 実行中のプロセス
    echo -e "\n[実行中のClaude CLIプロセス]"
    ps aux | grep claude | grep -v grep || echo "なし"
}

# 5分ごとに実行
while true; do
    check_worktree_health >> logs/health_check.log
    sleep 300
done
```

## クリーンアップルール

### Rule 15: 自動クリーンアップ

```bash
#!/bin/bash
# cleanup_worktrees.sh

cleanup_completed_worktrees() {
    local dry_run=${1:-false}
    
    echo "=== Worktree クリーンアップ ==="
    
    for worktree in worker/task_*; do
        if [ ! -d "$worktree" ]; then
            continue
        fi
        
        task_id=$(basename $worktree)
        branch=$(cd $worktree && git branch --show-current)
        
        # マージ済みチェック
        if git branch --merged main | grep -q "$branch"; then
            echo "✅ $task_id: マージ済み - クリーンアップ対象"
            
            if [ "$dry_run" = "false" ]; then
                # Worktree削除
                git worktree remove $worktree
                
                # ブランチ削除
                git branch -d $branch
                
                # ログアーカイブ
                mkdir -p logs/archive
                mv logs/task_${task_id}*.log logs/archive/
                
                echo "   削除完了: $worktree"
            fi
        else
            echo "⏳ $task_id: 未マージ - 保持"
        fi
    done
}

# ドライラン
cleanup_completed_worktrees true

# 実行確認
read -p "クリーンアップを実行しますか？ (y/N): " confirm
if [ "$confirm" = "y" ]; then
    cleanup_completed_worktrees false
fi
```

### Rule 16: 緊急クリーンアップ

```bash
# 異常時の強制クリーンアップ
emergency_cleanup() {
    echo "⚠️  緊急クリーンアップを開始します"
    
    # 1. すべてのClaude CLIプロセスを停止
    pkill -f "claude"
    
    # 2. Worktreeの強制削除
    for worktree in worker/task_*; do
        if [ -d "$worktree" ]; then
            git worktree remove --force $worktree
        fi
    done
    
    # 3. 参照の修復
    git worktree prune
    
    # 4. ガベージコレクション
    git gc --aggressive --prune=now
    
    echo "✅ 緊急クリーンアップ完了"
}
```

## 実践テンプレート

### Template 1: 基本的な並列実行

```bash
#!/bin/bash
# parallel_execute_template.sh

# 設定
TASKS=("auth-login" "auth-logout" "auth-session")
MAX_PARALLEL=3

# 準備
mkdir -p worker logs/execution logs/quality logs/summary

# Worktree作成
echo "=== Worktree作成 ==="
for i in "${!TASKS[@]}"; do
    task_id=$(printf "%03d" $((i+1)))
    git worktree add worker/task_${task_id} -b feature/${TASKS[$i]}
done

# 並列実行
echo "=== 並列実行開始 ==="
for i in "${!TASKS[@]}"; do
    task_id=$(printf "%03d" $((i+1)))
    (
        cd worker/task_${task_id}
        
        # メトリクス記録開始
        echo "[$(date)] Task ${task_id} started" >> ../../logs/execution/task_${task_id}.log
        
        # Claude CLI実行
        claude -p "Implement ${TASKS[$i]} functionality following TDD" \
            >> ../../logs/execution/task_${task_id}.log 2>&1
        
        # 品質チェック
        python ../../scripts/quality_gate_check.py \
            >> ../../logs/quality/task_${task_id}_quality.log 2>&1
        
        # メトリクス記録終了
        echo "[$(date)] Task ${task_id} completed" >> ../../logs/execution/task_${task_id}.log
    ) &
done

# 完了待機
wait

echo "=== 並列実行完了 ==="

# 結果サマリー
./generate_summary.sh > logs/summary/execution_$(date +%Y%m%d_%H%M%S).md
```

### Template 2: 段階的並列実行

```bash
#!/bin/bash
# phased_parallel_execution.sh

# Phase 1: 分析フェーズ（読み取り専用）
echo "=== Phase 1: 分析フェーズ ==="
parallel_analysis() {
    local components=("user" "payment" "notification")
    
    for component in "${components[@]}"; do
        (
            claude -p "Analyze ${component} service architecture and dependencies" \
                > "analysis/${component}_analysis.md"
        ) &
    done
    wait
}

# Phase 2: 設計フェーズ
echo "=== Phase 2: 設計フェーズ ==="
parallel_design() {
    local components=("user" "payment" "notification")
    
    for i in "${!components[@]}"; do
        task_id=$(printf "%03d" $((i+1)))
        (
            cd worker/task_${task_id}
            claude -p "Design improvements for ${components[$i]} based on analysis" \
                > "design/${components[$i]}_design.md"
        ) &
    done
    wait
}

# Phase 3: 実装フェーズ
echo "=== Phase 3: 実装フェーズ ==="
parallel_implementation() {
    local components=("user" "payment" "notification")
    
    for i in "${!components[@]}"; do
        task_id=$(printf "%03d" $((i+1)))
        (
            cd worker/task_${task_id}
            claude -p "Implement ${components[$i]} improvements based on design"
        ) &
    done
    wait
}

# 実行
parallel_analysis
parallel_design
parallel_implementation
```

### Template 3: 高度な並列実行管理

```python
#!/usr/bin/env python3
# advanced_parallel_manager.py

import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime

class GitWorktreeParallelManager:
    def __init__(self, project_root: Path, max_parallel: int = 3):
        self.project_root = project_root
        self.worker_dir = project_root / "worker"
        self.logs_dir = project_root / "logs"
        self.max_parallel = max_parallel
        self.semaphore = asyncio.Semaphore(max_parallel)
        
        # ロギング設定
        self._setup_logging()
        
    def _setup_logging(self):
        self.logs_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=self.logs_dir / "parallel_execution.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    async def create_worktree(self, task_id: str, branch_name: str) -> bool:
        """Worktreeを作成"""
        worktree_path = self.worker_dir / f"task_{task_id}"
        
        cmd = [
            "git", "worktree", "add",
            str(worktree_path),
            "-b", branch_name
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logging.error(f"Failed to create worktree for {task_id}: {stderr.decode()}")
                return False
                
            logging.info(f"Created worktree for {task_id} at {worktree_path}")
            return True
            
        except Exception as e:
            logging.error(f"Exception creating worktree for {task_id}: {str(e)}")
            return False
    
    async def execute_task(self, task_id: str, prompt: str) -> Dict[str, any]:
        """タスクを実行"""
        async with self.semaphore:
            worktree_path = self.worker_dir / f"task_{task_id}"
            start_time = datetime.now()
            
            # Claude CLI実行
            cmd = ["claude", "-p", prompt]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(worktree_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                duration = (datetime.now() - start_time).total_seconds()
                
                result = {
                    "task_id": task_id,
                    "success": process.returncode == 0,
                    "duration": duration,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
                
                # ログ記録
                self._save_task_log(task_id, result)
                
                return result
                
            except Exception as e:
                logging.error(f"Exception executing task {task_id}: {str(e)}")
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": str(e)
                }
    
    def _save_task_log(self, task_id: str, result: Dict):
        """タスクログを保存"""
        log_file = self.logs_dir / f"task_{task_id}_result.json"
        with open(log_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    async def run_quality_checks(self, task_id: str) -> bool:
        """品質チェックを実行"""
        worktree_path = self.worker_dir / f"task_{task_id}"
        
        checks = [
            ["pytest", "--cov=app", "--cov-fail-under=85"],
            ["flake8", "app/", "tests/", "--max-complexity=10"],
            ["black", "app/", "tests/", "--check"],
            ["isort", "app/", "tests/", "--check-only"]
        ]
        
        all_passed = True
        
        for check_cmd in checks:
            process = await asyncio.create_subprocess_exec(
                *check_cmd,
                cwd=str(worktree_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logging.warning(f"Quality check failed for {task_id}: {' '.join(check_cmd)}")
                all_passed = False
        
        return all_passed
    
    async def cleanup_worktree(self, task_id: str, force: bool = False) -> bool:
        """Worktreeをクリーンアップ"""
        worktree_path = self.worker_dir / f"task_{task_id}"
        
        cmd = ["git", "worktree", "remove"]
        if force:
            cmd.append("--force")
        cmd.append(str(worktree_path))
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logging.error(f"Failed to cleanup worktree for {task_id}: {stderr.decode()}")
                return False
                
            logging.info(f"Cleaned up worktree for {task_id}")
            return True
            
        except Exception as e:
            logging.error(f"Exception cleaning up worktree for {task_id}: {str(e)}")
            return False
    
    async def execute_parallel_tasks(self, tasks: List[Dict[str, str]]):
        """複数タスクを並列実行"""
        # Worktree作成
        create_tasks = []
        for task in tasks:
            create_task = self.create_worktree(task["id"], task["branch"])
            create_tasks.append(create_task)
        
        create_results = await asyncio.gather(*create_tasks)
        
        # タスク実行
        execute_tasks = []
        for i, task in enumerate(tasks):
            if create_results[i]:  # Worktree作成成功時のみ
                execute_task = self.execute_task(task["id"], task["prompt"])
                execute_tasks.append(execute_task)
        
        execute_results = await asyncio.gather(*execute_tasks)
        
        # 品質チェック
        quality_tasks = []
        for result in execute_results:
            if result["success"]:
                quality_task = self.run_quality_checks(result["task_id"])
                quality_tasks.append(quality_task)
        
        quality_results = await asyncio.gather(*quality_tasks)
        
        # 結果サマリー
        self._generate_summary(execute_results, quality_results)
        
        return execute_results
    
    def _generate_summary(self, execute_results: List[Dict], quality_results: List[bool]):
        """実行サマリーを生成"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(execute_results),
            "successful_tasks": sum(1 for r in execute_results if r["success"]),
            "quality_passed": sum(quality_results),
            "details": execute_results
        }
        
        summary_file = self.logs_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"Generated summary: {summary_file}")

# 使用例
async def main():
    manager = GitWorktreeParallelManager(Path.cwd(), max_parallel=3)
    
    tasks = [
        {
            "id": "001",
            "branch": "feature/auth-login",
            "prompt": "Implement login functionality with JWT authentication"
        },
        {
            "id": "002", 
            "branch": "feature/auth-logout",
            "prompt": "Implement logout functionality with token invalidation"
        },
        {
            "id": "003",
            "branch": "feature/auth-session",
            "prompt": "Implement session management with Redis"
        }
    ]
    
    results = await manager.execute_parallel_tasks(tasks)
    
    # クリーンアップ（オプション）
    for task in tasks:
        await manager.cleanup_worktree(task["id"])

if __name__ == "__main__":
    asyncio.run(main())
```

## トラブルシューティング

### 問題1: Worktree作成失敗

**症状**: `fatal: '...' is already checked out at '...'`

**解決策**:
```bash
# 既存worktreeの確認と削除
git worktree list
git worktree remove worker/task_XXX
```

### 問題2: ディスク容量不足

**症状**: Worktree作成時にエラー

**解決策**:
```bash
# 不要なworktreeの一括削除
git worktree prune
cleanup_completed_worktrees false

# ディスク使用量確認
df -h .
du -sh worker/*
```

### 問題3: マージコンフリクト

**症状**: 並列開発後のマージで競合

**解決策**:
```bash
# 競合の事前確認
for branch in feature/task-*; do
    echo "Checking $branch..."
    git merge --no-commit --no-ff $branch
    git merge --abort
done

# 順次マージ with 競合解決
for branch in feature/task-*; do
    git merge $branch || {
        echo "Conflict in $branch - resolving..."
        # 手動解決または自動解決ロジック
    }
done
```

### 問題4: プロセスのハング

**症状**: Claude CLIプロセスが応答しない

**解決策**:
```bash
# タイムアウト付き実行
timeout 1800 claude -p "タスクを実装"  # 30分でタイムアウト

# プロセス監視とキル
ps aux | grep claude
kill -TERM <PID>
```

## 📋 チェックリスト

### 実行前チェックリスト
- [ ] Gitリポジトリのクリーンな状態確認
- [ ] worker/ディレクトリの準備
- [ ] .gitignoreへのworker/追加
- [ ] 十分なディスク容量（タスク数 × リポジトリサイズ × 1.5）
- [ ] 並列度の決定（CPU数、メモリ量考慮）

### 実行中チェックリスト
- [ ] worktree作成の成功確認
- [ ] 各タスクの進行状況モニタリング
- [ ] リソース使用状況の監視
- [ ] エラーログの定期確認

### 実行後チェックリスト
- [ ] 全タスクの完了確認
- [ ] 品質チェックの合格確認
- [ ] マージ前の競合チェック
- [ ] worktreeのクリーンアップ
- [ ] 実行ログのアーカイブ

## 🎯 成功指標

1. **競合発生率**: 0%を維持
2. **並列実行効率**: 単一実行の3倍以上
3. **品質基準達成率**: 100%
4. **リソース使用効率**: CPU使用率60-80%
5. **エラー率**: 5%未満

## 📚 参照

- [Git Worktree公式ドキュメント](https://git-scm.com/docs/git-worktree)
- [memory-bank/git_worktree_parallel_development_verified.md](../../memory-bank/git_worktree_parallel_development_verified.md)
- [memory-bank/knowledge/ai_agent_delegation_patterns.md](../../memory-bank/knowledge/ai_agent_delegation_patterns.md)

---

**制定**: 2025-06-07  
**最終更新**: 2025-06-07  
**次回レビュー**: 2025-07-07