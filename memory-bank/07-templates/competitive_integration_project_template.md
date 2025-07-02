# 競争的統合プロジェクトテンプレート
# Competitive Integration Project Template

## KEYWORDS: competitive-framework, project-template, multi-agent-coordination, integration-workflow, reusable-pattern
## DOMAIN: project-management|templates|organizational-patterns
## PRIORITY: MEDIUM
## WHEN: 新規競争的プロジェクト計画時、統合タスクのテンプレートが必要な時、成功パターンの再利用時
## NAVIGATION: CLAUDE.md → competitive organization → project templates → this file

## RULE: 競争的統合プロジェクトは4フェーズ構成で実行し、各フェーズで品質ゲートを通過しなければならない

## 🎯 プロジェクトテンプレート概要

### テンプレートの目的
競争的組織フレームワークで実証された成功パターンを再利用可能なテンプレートとして体系化し、新規プロジェクトでの成功再現を可能にする。

### 適用シナリオ
```yaml
推奨適用ケース:
  高品質要求:
    - 品質基準が厳しいプロジェクト
    - ユーザー向け成果物の作成
    - 競合他社との差別化が必要
    
  複数アプローチの価値:
    - 最適解が不明な問題
    - イノベーションが期待されるタスク
    - リスクを分散したいプロジェクト
    
  リソース充分:
    - 14ペインの並列実行が可能
    - 複数Workerの協調管理が可能
    - 品質管理リソースが確保可能
```

## 🗺️ 4フェーズプロジェクト実行テンプレート

### Phase 1: プロジェクト初期化・戦略立案

#### タイムフレーム: 15-20分

```yaml
Phase1_初期化タスク:
  プロジェクトセットアップ:
    - [ ] tmuxセッション作成: competitive-[project-id]
    - [ ] 14ペイン構成の確立
    - [ ] git worktree環境のセットアップ
    - [ ] 共有ブリーフィングファイル作成
    
  戦略立案:
    - [ ] PMO/Consultantによる戦略立案
    - [ ] 3層価値統合アプローチの設計
    - [ ] Worker配置・役割分担の決定
    - [ ] 品質評価基準の設定
    
  リスク評価:
    - [ ] 技術的リスクの特定
    - [ ] コミュニケーションリスクの評価
    - [ ] スケジュールリスクの検討
    - [ ] リスク軽減策の策定
```

#### 実行スクリプト
```bash
#!/bin/bash
# Phase 1 Initialization Script

setup_competitive_project() {
    local project_id="$1"
    local project_title="$2"
    
    echo "🎆 Phase 1: Project Initialization"
    echo "Project ID: $project_id"
    echo "Title: $project_title"
    
    # tmuxセッション作成
    create_competitive_session "$project_id"
    
    # 共有ブリーフィング作成
    create_project_briefing "$project_id" "$project_title"
    
    # Worker配置設定
    assign_worker_roles "$project_id"
    
    # 品質ゲート設定
    setup_quality_gates "$project_id"
    
    echo "✅ Phase 1 completed successfully"
}

create_competitive_session() {
    local project_id="$1"
    local session_name="competitive-$project_id"
    
    # tmuxセッション作成
    tmux new-session -d -s "$session_name" -n "overview"
    
    # 14ペイン構成の作成
    # Window 0: 管理層 (Project Manager)
    
    # Window 1: 戦略層 (PMO/Consultant)
    tmux new-window -t "$session_name" -n "strategy"
    
    # Window 2: 実行層 (Task Execution Manager + Workers)
    tmux new-window -t "$session_name" -n "execution"
    tmux split-window -t "$session_name:execution" -h
    tmux split-window -t "$session_name:execution.0" -v
    tmux split-window -t "$session_name:execution.1" -v
    
    # Window 3: 評価層 (Task Review Manager + Reviewers)
    tmux new-window -t "$session_name" -n "review"
    tmux split-window -t "$session_name:review" -h
    tmux split-window -t "$session_name:review.0" -v
    tmux split-window -t "$session_name:review.1" -v
    
    # Window 4: 知識層 (Knowledge Manager + Extractors)
    tmux new-window -t "$session_name" -n "knowledge"
    tmux split-window -t "$session_name:knowledge" -h
    tmux split-window -t "$session_name:knowledge.0" -v
    tmux split-window -t "$session_name:knowledge.1" -v
    
    echo "✅ Competitive session '$session_name' created with 14-pane structure"
}

create_project_briefing() {
    local project_id="$1"
    local project_title="$2"
    
    local briefing_file="/tmp/competitive_briefing_${project_id}.md"
    
    cat > "$briefing_file" << EOF
# Competitive Project Briefing
## Project: $project_title
## ID: $project_id
## Date: $(date '+%Y-%m-%d %H:%M')

### Project Objectives
- [TO BE FILLED] Primary objective
- [TO BE FILLED] Success criteria
- [TO BE FILLED] Quality standards

### 3-Layer Value Integration Strategy
- Technical Excellence: 40% weight
- User Value: 30% weight  
- Practical Implementation: 30% weight

### Worker Assignments
- Worker 5: [TO BE ASSIGNED] Focus area
- Worker 8: [TO BE ASSIGNED] Focus area
- Worker 11: [TO BE ASSIGNED] Focus area

### Quality Evaluation Criteria
- Technical Review: Implementation accuracy, security, performance
- UX Review: Usability, accessibility, cognitive load
- Integration Review: Consistency, completeness, synergy

### Timeline
- Phase 1: Project initialization (15-20 min)
- Phase 2: Parallel execution (30-45 min)
- Phase 3: Quality evaluation (15-20 min)
- Phase 4: Integration & delivery (15-20 min)

---
*This briefing will be shared with all team members*
EOF

    echo "✅ Project briefing created: $briefing_file"
}
```

### Phase 2: 並列実行・競争的開発

#### タイムフレーム: 30-45分

```yaml
Phase2_並列実行:
  Worker配置管理:
    - [ ] 各Workerへのタスク割り当て
    - [ ] git worktree環境の分離確認
    - [ ] 依存関係の明確化
    - [ ] コミュニケーションプロトコル確立
    
  進捗監視:
    - [ ] 定期的な状態チェック（10分間隔）
    - [ ] ブロッカーの早期発見と解決
    - [ ] Worker間の協調支援
    - [ ] 品質基準の継続的確認
    
  リスク管理:
    - [ ] 技術的問題のエスカレーション
    - [ ] スケジュール遅延の対応
    - [ ] 品質問題の早期介入
    - [ ] コミュニケーション障害の解決
```

#### Worker配置テンプレート
```python
# Worker Assignment Template
class WorkerAssignmentTemplate:
    def __init__(self, project_id):
        self.project_id = project_id
        self.worker_specializations = {
            'worker_5': 'user_value_optimization',
            'worker_8': 'technical_implementation', 
            'worker_11': 'practical_application'
        }
        
    def assign_workers(self, project_requirements):
        """
        プロジェクト要件に基づくWorker割り当て
        """
        assignments = {}
        
        # Worker 5: ユーザー価値最適化
        assignments['worker_5'] = {
            'focus': 'User Value & Reader Experience',
            'objectives': [
                'Create reader-focused content structure',
                'Optimize for accessibility and engagement', 
                'Ensure practical applicability',
                'Maximize immediate value delivery'
            ],
            'success_criteria': [
                'Reader comprehension rate >90%',
                'Actionability score >85%',
                'Engagement metrics target achievement'
            ],
            'deliverables': [
                'User-centric content framework',
                'Accessibility-optimized presentation',
                'Value proposition validation'
            ]
        }
        
        # Worker 8: 技術実装最適化
        assignments['worker_8'] = {
            'focus': 'Technical Implementation & Accuracy',
            'objectives': [
                'Ensure technical correctness and precision',
                'Implement robust and scalable solutions',
                'Maintain security and performance standards',
                'Provide detailed implementation guidance'
            ],
            'success_criteria': [
                'Technical accuracy >99%',
                'Implementation completeness >95%',
                'Security compliance 100%'
            ],
            'deliverables': [
                'Technical implementation details',
                'Code examples and patterns',
                'Architecture and design specifications'
            ]
        }
        
        # Worker 11: 実践適用最適化
        assignments['worker_11'] = {
            'focus': 'Practical Application & Examples',
            'objectives': [
                'Create concrete implementation examples',
                'Develop step-by-step guides',
                'Ensure real-world applicability',
                'Provide troubleshooting guidance'
            ],
            'success_criteria': [
                'Example completeness >90%',
                'Step-by-step clarity >95%',
                'Real-world validation confirmed'
            ],
            'deliverables': [
                'Practical implementation examples',
                'Step-by-step execution guides',
                'Common issues and solutions'
            ]
        }
        
        return assignments
        
    def create_worker_briefings(self, assignments):
        """
        各Worker向けの詳細ブリーフィング作成
        """
        for worker_id, assignment in assignments.items():
            briefing_file = f"/tmp/worker_{worker_id}_briefing_{self.project_id}.md"
            
            with open(briefing_file, 'w') as f:
                f.write(f"""# Worker {worker_id} Assignment Briefing

## Project: {self.project_id}
## Focus Area: {assignment['focus']}

### Objectives
{chr(10).join(f'- {obj}' for obj in assignment['objectives'])}

### Success Criteria
{chr(10).join(f'- {criteria}' for criteria in assignment['success_criteria'])}

### Expected Deliverables
{chr(10).join(f'- {deliverable}' for deliverable in assignment['deliverables'])}

### Quality Standards
- Technical accuracy: Verify all code and implementations
- User value: Ensure immediate practical applicability
- Integration readiness: Prepare for seamless integration

### Communication Protocol
- Status updates every 10 minutes
- Immediate escalation of blockers
- Coordination through shared state files

---
*Execute with excellence. Your contribution is critical to project success.*
""")
                
            print(f"✅ Worker briefing created: {briefing_file}")
```

### Phase 3: 品質評価・レビュー

#### タイムフレーム: 15-20分

```yaml
Phase3_品質評価:
  Review Team配置:
    - [ ] Technical Reviewerのアサイン
    - [ ] UX Reviewerのアサイン
    - [ ] Integration Quality Reviewerのアサイン
    - [ ] 評価基準の確認と共有
    
  多角的評価実行:
    - [ ] 技術的正確性の評価（40%ウェイト）
    - [ ] UX/可読性の評価（30%ウェイト）
    - [ ] 統合品質の評価（30%ウェイト）
    - [ ] 総合品質スコアの算出
    
  改善提案・フィードバック:
    - [ ] 具体的改善提案の作成
    - [ ] 優先度付けと実装計画
    - [ ] フィードバックの統合チームへの伝達
    - [ ] 改善効果の検証計画
```

#### Review Teamテンプレート
```yaml
Review_Team_Configuration:
  Technical_Review:
    focus_areas:
      - 実装ギャップの特定
      - コード品質とセキュリティ
      - パフォーマンスとスケーラビリティ
      - 依存関係と保守性
    
    evaluation_criteria:
      - 技術的正確性: 25%
      - 実装可能性: 25%
      - コード品質: 25%
      - セキュリティ: 25%
    
  UX_Review:
    focus_areas:
      - 認知負荷の管理
      - 視覚的階層化
      - 情報密度の調整
      - アクセシビリティ
    
    evaluation_criteria:
      - 可読性: 30%
      - 認知負荷: 25%
      - アクセシビリティ: 25%
      - ユーザーエンゲージメント: 20%
    
  Integration_Quality_Review:
    focus_areas:
      - コンポーネント間の一貫性
      - テストスイートの完全性
      - エラー相関分析
      - シナジー効果の検証
    
    evaluation_criteria:
      - 統合品質: 40%
      - テストカバレッジ: 30%
      - エラー処理: 20%
      - シナジー効果: 10%
```

### Phase 4: 統合・最終納品

#### タイムフレーム: 15-20分

```yaml
Phase4_統合納品:
  統合作業:
    - [ ] Worker成果物の品質確認
    - [ ] Review指摘事項の必須反映
    - [ ] 3層価値統合アプローチの適用
    - [ ] シナジー効果の創出
    
  品質確認:
    - [ ] 最終品質スコアの確認（≥95%）
    - [ ] 全レビュー指摘事項の反映確認
    - [ ] 統合効果の検証
    - [ ] ユーザー価値の最終検証
    
  納品準備:
    - [ ] 成果物の最終フォーマット調整
    - [ ] ドキュメンテーションの完全性確認
    - [ ] プロジェクトサマリーの作成
    - [ ] 学習成果の抽出と記録
```

## 📊 品質評価フレームワークテンプレート

### 多次元評価指標
```python
class QualityEvaluationTemplate:
    def __init__(self):
        self.evaluation_dimensions = {
            'technical': {
                'weight': 0.40,
                'criteria': {
                    'accuracy': 0.25,
                    'implementability': 0.25,
                    'code_quality': 0.25,
                    'security': 0.25
                }
            },
            'ux': {
                'weight': 0.30,
                'criteria': {
                    'readability': 0.30,
                    'cognitive_load': 0.25,
                    'accessibility': 0.25,
                    'engagement': 0.20
                }
            },
            'integration': {
                'weight': 0.30,
                'criteria': {
                    'consistency': 0.40,
                    'test_coverage': 0.30,
                    'error_handling': 0.20,
                    'synergy': 0.10
                }
            }
        }
        
    def evaluate_worker_output(self, worker_id, output_data):
        """
        Worker成果物の多次元評価
        """
        evaluation_results = {}
        
        for dimension, config in self.evaluation_dimensions.items():
            dimension_score = 0
            dimension_details = {}
            
            for criterion, weight in config['criteria'].items():
                criterion_score = self.evaluate_criterion(
                    dimension, criterion, output_data
                )
                dimension_details[criterion] = criterion_score
                dimension_score += criterion_score * weight
                
            evaluation_results[dimension] = {
                'score': dimension_score,
                'weight': config['weight'],
                'details': dimension_details
            }
            
        # 総合スコアの算出
        overall_score = sum(
            result['score'] * result['weight'] 
            for result in evaluation_results.values()
        )
        
        return {
            'worker_id': worker_id,
            'overall_score': overall_score,
            'dimensions': evaluation_results,
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
    def generate_improvement_suggestions(self, evaluation_results):
        """
        評価結果に基づく改善提案生成
        """
        suggestions = []
        
        for dimension, result in evaluation_results['dimensions'].items():
            if result['score'] < 0.85:  # 85%未満の場合
                low_criteria = [
                    criterion for criterion, score in result['details'].items()
                    if score < 0.80
                ]
                
                if low_criteria:
                    suggestions.append({
                        'dimension': dimension,
                        'priority': 'high' if result['score'] < 0.70 else 'medium',
                        'criteria': low_criteria,
                        'improvement_actions': self.get_improvement_actions(
                            dimension, low_criteria
                        )
                    })
                    
        return suggestions
```

## 📋 プロジェクトチェックリストテンプレート

### プロジェクト開始前チェックリスト
```yaml
Pre_Project_Checklist:
  環境準備:
    - [ ] tmuxバージョン確認（≪3.0）
    - [ ] git worktree機能の動作確認
    - [ ] 必要なディレクトリ構造の存在確認
    - [ ] 権限設定の確認（/tmp書き込み可能）
    
  チーム準備:
    - [ ] プロジェクト目標の明確化
    - [ ] 品質基準の合意形成
    - [ ] コミュニケーションプロトコルの共有
    - [ ] 緊急時エスカレーション手順の確認
    
  プロジェクト設定:
    - [ ] タイムラインの現実性確認
    - [ ] リスク評価と軽減策の策定
    - [ ] 成功指標の定量化
    - [ ] フォールバックプランの策定
```

### 各フェーズ完了ゲート
```yaml
Phase_Completion_Gates:
  Phase1_Gate:
    mandatory_criteria:
      - [ ] 14ペイン構成の確立
      - [ ] 全Workerへのブリーフィング完了
      - [ ] 品質評価基準の合意
      - [ ] コミュニケーションテスト成功
    pass_threshold: 100%
    
  Phase2_Gate:
    mandatory_criteria:
      - [ ] 全Workerの成果物産出確認
      - [ ] 品質基準の基本適合
      - [ ] コミュニケーションログの確認
      - [ ] 重大問題の不在確認
    pass_threshold: 95%
    
  Phase3_Gate:
    mandatory_criteria:
      - [ ] 全Reviewチームの評価完了
      - [ ] 改善提案の文書化
      - [ ] 品質スコア≥85%達成
      - [ ] Critical問題の完全解決
    pass_threshold: 90%
    
  Phase4_Gate:
    mandatory_criteria:
      - [ ] 全レビュー指摘事項の反映
      - [ ] 最終品質スコア≥95%
      - [ ] 統合効果の実証
      - [ ] プロジェクト成果の確定
    pass_threshold: 100%
```

## 🚀 プロジェクト起動スクリプト

### ワンコマンド起動
```bash
#!/bin/bash
# Competitive Integration Project Launcher

launch_competitive_project() {
    local project_title="$1"
    local project_description="$2"
    
    if [ -z "$project_title" ]; then
        echo "Usage: launch_competitive_project <title> [description]"
        echo "Example: launch_competitive_project 'AI Integration Guide' 'Comprehensive guide for AI agent coordination'"
        return 1
    fi
    
    # プロジェクトID生成
    local project_id=$(echo "$project_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g')
    local timestamp=$(date +%Y%m%d_%H%M)
    project_id="${project_id}_${timestamp}"
    
    echo "🎆 Launching Competitive Integration Project"
    echo "Project: $project_title"
    echo "ID: $project_id"
    echo "Description: ${project_description:-'No description provided'}"
    echo ""
    
    # Phase 1: プロジェクト初期化
    echo "📚 Phase 1: Project Initialization"
    setup_competitive_project "$project_id" "$project_title"
    
    # Phase 2: Worker配置
    echo "🛠️ Phase 2: Worker Assignment"
    assign_and_brief_workers "$project_id" "$project_description"
    
    # Phase 3: 実行監視開始
    echo "📋 Phase 3: Execution Monitoring"
    start_project_monitoring "$project_id"
    
    echo ""
    echo "✅ Project '$project_title' successfully launched!"
    echo "Session: competitive-$project_id"
    echo "Monitoring: /tmp/competitive_monitoring_$project_id.log"
    echo ""
    echo "Next steps:"
    echo "1. Monitor worker progress (automatic monitoring started)"
    echo "2. Review outputs as they become available"
    echo "3. Proceed with integration when all workers complete"
    
    # プロジェクト情報の永続化
    save_project_metadata "$project_id" "$project_title" "$project_description"
}

# プロジェクトメタデータ保存
save_project_metadata() {
    local project_id="$1"
    local project_title="$2"
    local project_description="$3"
    
    local metadata_file="/tmp/competitive_project_${project_id}_metadata.json"
    
    cat > "$metadata_file" << EOF
{
  "project_id": "$project_id",
  "title": "$project_title",
  "description": "$project_description",
  "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "template_version": "1.0",
  "phases": {
    "phase1": {
      "name": "Initialization", 
      "status": "completed",
      "completion_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "phase2": {
      "name": "Parallel Execution",
      "status": "in_progress",
      "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    },
    "phase3": {
      "name": "Quality Evaluation",
      "status": "pending"
    },
    "phase4": {
      "name": "Integration & Delivery",
      "status": "pending"
    }
  },
  "expected_deliverables": [
    "High-quality integrated content",
    "Multi-dimensional quality evaluation",
    "Lessons learned documentation",
    "Reusable process improvements"
  ]
}
EOF

    echo "Project metadata saved: $metadata_file"
}

# Usage example
# launch_competitive_project "AI Agent Coordination Guide" "Comprehensive implementation guide for advanced AI agent coordination systems"
```

## 📊 成果測定テンプレート

### KPI設定ガイド
```yaml
Project_Success_Metrics:
  品質指標:
    target_overall_quality: ">95%"
    technical_accuracy: ">99%"
    user_value_score: ">90%"
    integration_effectiveness: ">95%"
    
  効率指標:
    project_completion_time: "<90 minutes"
    worker_parallel_efficiency: ">80%"
    review_cycle_time: "<20 minutes"
    issue_resolution_time: "<15 minutes"
    
  協調指標:
    communication_success_rate: ">95%"
    coordination_overhead: "<15%"
    conflict_resolution_efficiency: ">90%"
    knowledge_sharing_effectiveness: ">85%"
    
  イノベーション指標:
    unique_solution_generation: ">3 approaches"
    synergy_effect_achievement: ">200% vs single approach"
    creative_problem_solving: ">2 novel methods"
    cross_pollination_instances: ">5 idea exchanges"
```

### 成果レポートテンプレート
```markdown
# Competitive Integration Project Report Template

## Project Overview
- **Project ID**: [AUTO-GENERATED]
- **Title**: [USER-PROVIDED]
- **Start Time**: [TIMESTAMP]
- **Completion Time**: [TIMESTAMP]
- **Total Duration**: [CALCULATED]

## Executive Summary
### Key Achievements
- [ ] High-quality deliverable creation
- [ ] Multi-dimensional quality validation
- [ ] Successful parallel coordination
- [ ] Effective knowledge integration

### Quantitative Results
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Overall Quality | >95% | [X]% | [PASS/FAIL] |
| Technical Accuracy | >99% | [X]% | [PASS/FAIL] |
| Completion Time | <90min | [X]min | [PASS/FAIL] |
| Integration Effect | >95% | [X]% | [PASS/FAIL] |

## Phase-by-Phase Analysis
### Phase 1: Initialization ([X] minutes)
- Setup efficiency: [X]%
- Communication establishment: [SUCCESS/ISSUES]
- Worker briefing effectiveness: [X]%

### Phase 2: Parallel Execution ([X] minutes)
- Worker output quality: [X]%
- Coordination efficiency: [X]%
- Issue resolution count: [X]

### Phase 3: Quality Evaluation ([X] minutes)
- Review comprehensiveness: [X]%
- Improvement suggestions: [X] items
- Review cycle efficiency: [X]%

### Phase 4: Integration & Delivery ([X] minutes)
- Integration completeness: [X]%
- Final quality achievement: [X]%
- Synergy effect measurement: [X]%

## Lessons Learned
### What Worked Well
1. [SPECIFIC SUCCESS FACTOR]
2. [SPECIFIC SUCCESS FACTOR]
3. [SPECIFIC SUCCESS FACTOR]

### Areas for Improvement
1. [SPECIFIC IMPROVEMENT AREA]
2. [SPECIFIC IMPROVEMENT AREA]
3. [SPECIFIC IMPROVEMENT AREA]

### Recommendations for Future Projects
1. [ACTIONABLE RECOMMENDATION]
2. [ACTIONABLE RECOMMENDATION]
3. [ACTIONABLE RECOMMENDATION]

## Return on Investment
- **Time Investment**: [X] hours
- **Quality Improvement**: [X]% vs single-agent approach
- **Innovation Factor**: [X]x more creative solutions
- **Reusability**: [X] reusable components created

---
*Report generated automatically from project execution data*
```

## METRICS: テンプレート効果測定

```yaml
Template_Effectiveness_Metrics:
  reusability_score:
    formula: successful_projects / total_template_uses
    target: >80%
    measurement: project_success_rate
    
  setup_efficiency:
    formula: actual_setup_time / planned_setup_time
    target: <1.2
    measurement: phase1_duration_ratio
    
  quality_consistency:
    formula: stdev(project_quality_scores)
    target: <5%
    measurement: quality_variance_across_projects
    
  learning_acceleration:
    formula: (project_n_duration - project_1_duration) / project_1_duration
    target: >30% improvement by 5th use
    measurement: learning_curve_slope
```

## RELATED:
- memory-bank/02-organization/competitive_framework_lessons_learned.md
- memory-bank/02-organization/competitive_organization_framework.md
- memory-bank/04-quality/quality_assurance_process_improvement.md
- memory-bank/09-meta/session_continuity_task_management.md

---
*Creation Date: 2025-07-01*
*Based On: Competitive Organization Framework Success Patterns*
*Template Version: 1.0 - Production Ready*