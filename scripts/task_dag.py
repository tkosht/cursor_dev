#!/usr/bin/env python3
"""
Task DAG (Directed Acyclic Graph) Management System
TodoWriteとの統合によるタスク構造化・委譲最適化システム
"""

import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path


class TaskType(Enum):
    """タスクタイプ分類"""
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    INFRASTRUCTURE = "infrastructure"
    RESEARCH = "research"


class TaskStatus(Enum):
    """タスクステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class TaskNode:
    """Task DAGの個別ノード"""
    id: str
    description: str
    task_type: TaskType
    status: TaskStatus
    priority: str  # "high", "medium", "low"
    dependencies: List[str]  # 依存するタスクのID
    complexity: int  # 1-10スケール
    estimated_duration: float  # 推定所要時間（分）
    delegation_score: Optional[int] = None  # 委譲推奨スコア（1-10）
    
    def __post_init__(self):
        """初期化後の処理"""
        if self.delegation_score is None:
            self.delegation_score = self._calculate_delegation_score()
    
    def _calculate_delegation_score(self) -> int:
        """委譲スコアの自動計算"""
        score = 0
        
        # 複雑度による加点 (0-3点)
        if self.complexity >= 7:
            score += 3
        elif self.complexity >= 5:
            score += 2
        elif self.complexity >= 3:
            score += 1
        
        # タスクタイプによる加点 (0-2点)
        if self.task_type in [TaskType.TESTING, TaskType.DOCUMENTATION]:
            score += 2  # 定型作業は委譲しやすい
        elif self.task_type == TaskType.RESEARCH:
            score += 1
        
        # 独立性による加点 (0-2点)
        if len(self.dependencies) == 0:
            score += 2  # 依存関係なしは委譲しやすい
        elif len(self.dependencies) <= 2:
            score += 1
        
        # 推定時間による加点 (0-2点)
        if self.estimated_duration >= 60:  # 1時間以上
            score += 2
        elif self.estimated_duration >= 30:  # 30分以上
            score += 1
        
        # 優先度による調整 (0-1点)
        if self.priority == "low":
            score += 1  # 低優先度は委譲しやすい
        
        return min(score, 10)  # 最大10点


@dataclass
class TaskDAG:
    """Task Directed Acyclic Graph"""
    nodes: Dict[str, TaskNode]
    edges: List[Tuple[str, str]]  # (from_id, to_id)
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {
                "created_at": str(uuid.uuid4()),
                "version": "1.0",
                "total_nodes": len(self.nodes)
            }
    
    def add_node(self, node: TaskNode) -> bool:
        """ノード追加"""
        if node.id in self.nodes:
            return False
        
        self.nodes[node.id] = node
        self.metadata["total_nodes"] = len(self.nodes)
        return True
    
    def add_dependency(self, from_id: str, to_id: str) -> bool:
        """依存関係追加"""
        if from_id not in self.nodes or to_id not in self.nodes:
            return False
        
        # 循環依存チェック
        if self._creates_cycle(from_id, to_id):
            return False
        
        self.edges.append((from_id, to_id))
        if to_id not in self.nodes[to_id].dependencies:
            self.nodes[to_id].dependencies.append(from_id)
        
        return True
    
    def _creates_cycle(self, from_id: str, to_id: str) -> bool:
        """循環依存チェック"""
        visited = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in visited:
                return True
            if node_id == from_id:
                return True
            
            visited.add(node_id)
            for edge in self.edges:
                if edge[1] == node_id:  # この node_id に向かうエッジ
                    if dfs(edge[0]):
                        return True
            visited.remove(node_id)
            return False
        
        return dfs(to_id)
    
    def get_independent_nodes(self) -> List[TaskNode]:
        """並列実行可能な独立ノードを取得"""
        return [node for node in self.nodes.values() 
                if len(node.dependencies) == 0 and node.status == TaskStatus.PENDING]
    
    def get_delegation_candidates(self, threshold: int = 6) -> List[TaskNode]:
        """委譲候補ノードを取得"""
        return [node for node in self.nodes.values() 
                if node.delegation_score >= threshold and node.status == TaskStatus.PENDING]
    
    def get_execution_order(self) -> List[List[str]]:
        """実行順序を取得（各レベルは並列実行可能）"""
        levels = []
        remaining_nodes = set(self.nodes.keys())
        completed_nodes = set()
        
        while remaining_nodes:
            # 依存関係が満たされたノードを特定
            ready_nodes = []
            for node_id in remaining_nodes:
                node = self.nodes[node_id]
                if all(dep in completed_nodes for dep in node.dependencies):
                    ready_nodes.append(node_id)
            
            if not ready_nodes:
                # 循環依存または未解決の依存関係
                break
            
            levels.append(ready_nodes)
            remaining_nodes -= set(ready_nodes)
            completed_nodes.update(ready_nodes)
        
        return levels
    
    def to_dict(self) -> Dict:
        """辞書形式への変換"""
        return {
            "nodes": {node_id: asdict(node) for node_id, node in self.nodes.items()},
            "edges": self.edges,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskDAG':
        """辞書からの復元"""
        nodes = {}
        for node_id, node_data in data["nodes"].items():
            # Enum変換
            node_data["task_type"] = TaskType(node_data["task_type"])
            node_data["status"] = TaskStatus(node_data["status"])
            nodes[node_id] = TaskNode(**node_data)
        
        dag = cls(
            nodes=nodes,
            edges=data["edges"],
            metadata=data.get("metadata", {})
        )
        return dag
    
    def save_to_file(self, filepath: str):
        """ファイルへの保存"""
        # Enum を文字列に変換してJSON対応
        data = self.to_dict()
        for node_data in data["nodes"].values():
            node_data["task_type"] = node_data["task_type"].value
            node_data["status"] = node_data["status"].value
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'TaskDAG':
        """ファイルからの読み込み"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


def create_dag_from_todos(todos: List[Dict]) -> TaskDAG:
    """TodoWriteのデータからTask DAGを生成"""
    dag = TaskDAG(nodes={}, edges=[])
    
    # ノード作成
    for todo in todos:
        task_type = _infer_task_type(todo.get("content", ""))
        complexity = _estimate_complexity(todo.get("content", ""))
        duration = _estimate_duration(todo.get("content", ""), complexity)
        
        node = TaskNode(
            id=todo.get("id", str(uuid.uuid4())),
            description=todo.get("content", ""),
            task_type=task_type,
            status=TaskStatus(todo.get("status", "pending")),
            priority=todo.get("priority", "medium"),
            dependencies=[],  # 初期は空、後で推論
            complexity=complexity,
            estimated_duration=duration
        )
        
        dag.add_node(node)
    
    # 依存関係推論（シンプルな実装）
    _infer_dependencies(dag, todos)
    
    return dag


def _infer_task_type(description: str) -> TaskType:
    """タスク説明からタイプを推論"""
    desc_lower = description.lower()
    
    if any(word in desc_lower for word in ["test", "テスト", "検証", "verify"]):
        return TaskType.TESTING
    elif any(word in desc_lower for word in ["doc", "document", "ドキュメント", "readme", "説明"]):
        return TaskType.DOCUMENTATION
    elif any(word in desc_lower for word in ["review", "レビュー", "確認", "check"]):
        return TaskType.REVIEW
    elif any(word in desc_lower for word in ["setup", "config", "設定", "環境", "infrastructure"]):
        return TaskType.INFRASTRUCTURE
    elif any(word in desc_lower for word in ["research", "調査", "分析", "analysis", "study"]):
        return TaskType.RESEARCH
    else:
        return TaskType.IMPLEMENTATION


def _estimate_complexity(description: str) -> int:
    """タスク説明から複雑度を推定"""
    desc_lower = description.lower()
    
    # キーワードベースの推定
    complex_keywords = ["architecture", "design", "integration", "algorithm", "optimization"]
    simple_keywords = ["fix", "update", "add", "remove", "format"]
    
    if any(word in desc_lower for word in complex_keywords):
        return 7 + min(len([w for w in complex_keywords if w in desc_lower]), 3)
    elif any(word in desc_lower for word in simple_keywords):
        return 2 + min(len([w for w in simple_keywords if w in desc_lower]), 3)
    else:
        return 5  # デフォルト


def _estimate_duration(description: str, complexity: int) -> float:
    """推定所要時間（分）"""
    base_time = complexity * 10  # 複雑度1 = 10分
    
    # タスクタイプによる調整
    desc_lower = description.lower()
    if any(word in desc_lower for word in ["implement", "create", "build"]):
        base_time *= 1.5
    elif any(word in desc_lower for word in ["fix", "update", "modify"]):
        base_time *= 0.8
    
    return base_time


def _infer_dependencies(dag: TaskDAG, todos: List[Dict]):
    """依存関係の推論（シンプルな実装）"""
    # 優先度とタスクタイプベースの依存関係推論
    high_priority_nodes = [node_id for node_id, node in dag.nodes.items() 
                          if node.priority == "high"]
    
    for node_id, node in dag.nodes.items():
        if node.priority in ["medium", "low"] and high_priority_nodes:
            # 低・中優先度は高優先度に依存する可能性
            for dep_id in high_priority_nodes[:1]:  # 最初の高優先度に依存
                if dep_id != node_id:
                    dag.add_dependency(dep_id, node_id)


def main():
    """テスト用メイン関数"""
    # サンプルTodoデータ
    sample_todos = [
        {"id": "1", "content": "プロジェクト設計", "status": "pending", "priority": "high"},
        {"id": "2", "content": "テストケース作成", "status": "pending", "priority": "medium"},
        {"id": "3", "content": "ドキュメント更新", "status": "pending", "priority": "low"},
        {"id": "4", "content": "コード実装", "status": "pending", "priority": "high"}
    ]
    
    # DAG生成
    dag = create_dag_from_todos(sample_todos)
    
    # 結果表示
    print("=== Task DAG Analysis ===")
    print(f"Total nodes: {len(dag.nodes)}")
    print(f"Independent nodes: {len(dag.get_independent_nodes())}")
    print(f"Delegation candidates: {len(dag.get_delegation_candidates())}")
    
    # 実行順序表示
    execution_order = dag.get_execution_order()
    print("\n=== Execution Order ===")
    for level, nodes in enumerate(execution_order):
        print(f"Level {level + 1}: {nodes}")
    
    # 委譲候補表示
    print("\n=== Delegation Candidates ===")
    for node in dag.get_delegation_candidates():
        print(f"- {node.description} (Score: {node.delegation_score})")
    
    # ファイル保存テスト
    dag.save_to_file("sample_dag.json")
    print("\n✅ DAG saved to sample_dag.json")


if __name__ == "__main__":
    main()