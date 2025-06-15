# 検証スクリプト設計ルール

最終更新: 2025-06-04

## 📋 概要

ドキュメント正確性検証スクリプトにおける例文・エラー例の除外パターン標準化と、効果的な検証システム設計のルール。

## 🎯 設計基本原則

### 1. 精度と実用性のバランス
- **過検出の回避**: 例文やサンプルコードを除外
- **見逃し防止**: 真の問題は確実に検出
- **保守性重視**: パターンの追加・修正が容易

### 2. 明確性の原則
- **意図の明確化**: なぜそのパターンを除外するかを明記
- **範囲の限定**: 過度に広範囲な除外を避ける
- **文脈考慮**: 文書の種類・セクション別の判定

## 📝 標準除外パターン

### 1. エラー表示・警告マーカー

**パターン配列**:
```python
ERROR_WARNING_MARKERS = [
    '❌ ERROR', '⚠️ WARNING', '🚨 CRITICAL',
    'ERROR:', 'WARNING:', 'CRITICAL:',
    '# Note:', '注意：', 'Note:',
    'エラー例', 'WARNING例', '失敗例'
]
```

**使用例**:
```python
if any(marker in block for marker in ERROR_WARNING_MARKERS):
    continue  # この行/ブロックは検証対象から除外
```

### 2. 例文・サンプルマーカー

**パターン配列**:
```python
EXAMPLE_MARKERS = [
    '# 例:', '# Example:', '# サンプル:', '# Sample:',
    '例：', 'Example:', 'Sample:', 'サンプル：',
    '例文', 'サンプルコード', 'example code',
    '以下は例', '以下の例', 'for example', 'e.g.',
    '```example', '```sample', '<!-- example', '<!-- sample'
]
```

### 3. 修正前・バッドプラクティス

**パターン配列**:
```python
BAD_PRACTICE_MARKERS = [
    '修正前', '修正前:', 'Before fix:',
    '悪い例', 'Bad example:', '間違った例',
    'バッドプラクティス', 'bad practice',
    '非推奨', 'deprecated', 'obsolete'
]
```

### 4. 実行結果例・デモ出力

**パターン配列**:
```python
OUTPUT_EXAMPLE_MARKERS = [
    '実行結果例', '出力例', 'Output example:',
    '以下は実行結果', '以下の出力', 'sample output',
    '実行時の出力', 'コマンド実行例',
    'Example output:', 'Sample result:'
]
```

### 5. プロジェクト固有の廃止パターン

**パターン配列**:
```python
DEPRECATED_PROJECT_PATTERNS = [
    'a2a_prototype', 'a2a_mvp',  # 旧プロジェクト構造
    'utils.helper', 'utils.config',  # 廃止モジュール
    'old_api', 'legacy_',  # レガシーコード例
]
```

## 🛠️ 実装パターン

### 1. 基本的な除外チェック

```python
def should_exclude_block(self, block: str) -> bool:
    """ブロック全体を除外すべきかチェック"""
    
    # 全除外パターンを統合
    all_exclude_patterns = (
        self.ERROR_WARNING_MARKERS +
        self.EXAMPLE_MARKERS +
        self.BAD_PRACTICE_MARKERS +
        self.OUTPUT_EXAMPLE_MARKERS +
        self.DEPRECATED_PROJECT_PATTERNS
    )
    
    return any(marker in block for marker in all_exclude_patterns)
```

### 2. 行レベルの除外チェック

```python
def should_exclude_line(self, line: str, context_lines: List[str]) -> bool:
    """個別行を除外すべきかチェック（文脈考慮）"""
    
    # 直接的なマーカーチェック
    if any(marker in line for marker in self.ERROR_WARNING_MARKERS):
        return True
    
    # 文脈考慮（前後の行もチェック）
    context = '\n'.join(context_lines)
    if any(marker in context for marker in self.EXAMPLE_MARKERS):
        return True
    
    return False
```

### 3. セクション別の除外判定

```python
def get_document_section(self, line_number: int, lines: List[str]) -> str:
    """文書内のセクションを特定"""
    
    # 見出しを逆検索してセクションを特定
    for i in range(line_number - 1, -1, -1):
        if lines[i].startswith('#'):
            return lines[i].strip()
    return ""

def should_exclude_by_section(self, section: str) -> bool:
    """セクション名による除外判定"""
    
    exclude_sections = [
        '実行結果例', 'Example Output', 'エラー例',
        'トラブルシューティング', 'Troubleshooting',
        'よくある問題', 'Common Issues'
    ]
    
    return any(exclude in section for exclude in exclude_sections)
```

## 📊 パターン管理のベストプラクティス

### 1. パターンの階層化

```python
class ExclusionPatterns:
    """除外パターンの階層管理"""
    
    def __init__(self):
        # 基本パターン（変更頻度低）
        self.CORE_PATTERNS = [
            '❌ ERROR', '⚠️ WARNING', '# Example:'
        ]
        
        # プロジェクト固有パターン（変更頻度中）
        self.PROJECT_PATTERNS = [
            'a2a_prototype', 'legacy_config'
        ]
        
        # 一時的パターン（定期見直し対象）
        self.TEMPORARY_PATTERNS = [
            'temp_exclude_pattern'
        ]
    
    def get_all_patterns(self) -> List[str]:
        return (self.CORE_PATTERNS + 
                self.PROJECT_PATTERNS + 
                self.TEMPORARY_PATTERNS)
```

### 2. パターンの文書化

```python
PATTERN_DOCUMENTATION = {
    '❌ ERROR': {
        'purpose': 'エラー表示例の除外',
        'added_date': '2025-06-04',
        'reason': 'ドキュメント内のエラー例が誤検出される',
        'review_cycle': '6ヶ月'
    },
    'a2a_prototype': {
        'purpose': '廃止プロジェクト構造の除外',
        'added_date': '2025-06-04',
        'reason': '旧構造のサンプルコードが残存',
        'review_cycle': '3ヶ月（削除予定）'
    }
}
```

### 3. 動的パターン生成

```python
def generate_context_aware_patterns(self, file_path: Path) -> List[str]:
    """ファイル種別に応じた動的パターン生成"""
    
    patterns = self.CORE_PATTERNS.copy()
    
    # README.mdの場合
    if file_path.name == 'README.md':
        patterns.extend([
            'インストール例', 'Installation example',
            'クイックスタート', 'Quick start'
        ])
    
    # 技術仕様書の場合
    if 'specification' in str(file_path) or 'spec' in str(file_path):
        patterns.extend([
            'サンプルレスポンス', 'Sample response',
            'API例', 'API example'
        ])
    
    return patterns
```

## 🔍 品質保証

### 1. パターン効果の測定

```python
class PatternEffectivenessTracker:
    """パターン効果の追跡"""
    
    def __init__(self):
        self.exclusion_stats = {}
        self.false_positive_count = 0
        self.true_positive_count = 0
    
    def track_exclusion(self, pattern: str, file_path: str, line: str):
        """除外実行の記録"""
        if pattern not in self.exclusion_stats:
            self.exclusion_stats[pattern] = []
        
        self.exclusion_stats[pattern].append({
            'file': file_path,
            'line': line,
            'timestamp': datetime.now()
        })
    
    def generate_effectiveness_report(self) -> Dict:
        """効果レポートの生成"""
        return {
            'pattern_usage': self.exclusion_stats,
            'false_positive_rate': self.false_positive_count / self.total_checks,
            'pattern_efficiency': len(self.exclusion_stats)
        }
```

### 2. 定期的なパターン見直し

```python
def review_patterns_quarterly():
    """四半期パターンレビュー"""
    
    # 使用頻度の低いパターンを特定
    low_usage_patterns = identify_low_usage_patterns()
    
    # 新しい誤検出パターンを分析
    new_false_positives = analyze_recent_false_positives()
    
    # レビューレポートを生成
    generate_pattern_review_report(low_usage_patterns, new_false_positives)
```

## 🚀 拡張・改善ガイドライン

### 1. 新パターン追加の基準

**追加条件**:
- **再現性**: 同様の問題が3回以上発生
- **影響度**: 複数ファイルまたは頻繁な誤検出
- **妥当性**: 除外が論理的に正当

**追加プロセス**:
1. 問題の詳細分析
2. 最小限のパターン設計
3. テスト実行による効果確認
4. ドキュメント更新
5. チームレビュー

### 2. パターンの最適化

```python
def optimize_patterns():
    """パターンの最適化"""
    
    # 重複パターンの統合
    deduplicated = remove_duplicate_patterns()
    
    # 正規表現への変換（高速化）
    regex_patterns = convert_to_regex_where_beneficial()
    
    # パフォーマンステスト
    performance_test_results = benchmark_pattern_matching()
    
    return optimized_patterns
```

### 3. 多言語対応

```python
MULTILINGUAL_PATTERNS = {
    'ja': ['例：', 'サンプル：', 'エラー例'],
    'en': ['Example:', 'Sample:', 'Error example'],
    'zh': ['例子：', '示例：', '错误示例']
}

def get_localized_patterns(locale: str) -> List[str]:
    """ロケール別パターン取得"""
    return MULTILINGUAL_PATTERNS.get(locale, MULTILINGUAL_PATTERNS['en'])
```

## 📈 継続的改善

### 改善サイクル
1. **月次**: 新しい誤検出の確認
2. **四半期**: パターン効果の分析・見直し
3. **年次**: 設計方針の根本的レビュー

### 成功指標
- **誤検出率**: < 5%
- **見逃し率**: < 1%
- **パターン追加頻度**: 月1回以下
- **開発者満足度**: 定期アンケート実施

---

**作成背景**: verify_accuracy.py の改善プロセスで得られた知見を、再利用可能なルールとして標準化