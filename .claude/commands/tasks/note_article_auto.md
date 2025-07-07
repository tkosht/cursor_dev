# Smart Note Article Creator

## 👤 ROLE
あなたは、Smart Note Article Creator です。ユーザーの状況に応じて最適な記事作成方式を自動選択します。

## 🎯 自動判定システム

### Step 1: 状況分析（30秒）

```bash
# ユーザー状況の自動分析
analyze_user_context() {
    echo "📊 最適な記事作成方式を分析中..."
    
    # トピックの複雑性分析
    local topic="$ARGUMENTS"
    local complexity_score=0
    
    # 複雑性指標
    [[ "$topic" =~ "実装|システム|アーキテクチャ" ]] && complexity_score=$((complexity_score + 2))
    [[ "$topic" =~ "比較|分析|評価" ]] && complexity_score=$((complexity_score + 2))  
    [[ "$topic" =~ "事例|体験|経験" ]] && complexity_score=$((complexity_score + 1))
    [[ "$topic" =~ "基本|簡単|概要" ]] && complexity_score=$((complexity_score - 1))
    
    # 推奨方式の決定
    if [ $complexity_score -le 1 ]; then
        echo "🚀 推奨: Quick版（5-10分）- シンプルな情報共有に最適"
        return 1
    elif [ $complexity_score -le 3 ]; then
        echo "⚖️ 推奨: Standard版（15-20分）- バランス重視"
        return 2
    else
        echo "🏆 推奨: 高品質版（30-45分）- 包括的で詳細な記事"
        return 3
    fi
}
```

### Step 2: 自動実行または確認

```bash
# 自動実行ロジック
execute_optimal_approach() {
    analyze_user_context
    local recommended_level=$?
    
    case $recommended_level in
        1)
            echo "✅ Quick版で記事を作成します"
            # Quick版のロジック実行
            create_quick_article "$ARGUMENTS"
            ;;
        2)
            echo "✅ Standard版で記事を作成します"
            echo "💡 より簡単にしたい場合は /note_article_quick を、"
            echo "   より高品質にしたい場合は /note_article を使用してください"
            # Standard版のロジック実行
            create_standard_article "$ARGUMENTS"
            ;;
        3)
            echo "✅ 高品質版での作成を推奨します"
            echo "⏰ 予想所要時間: 30-45分"
            echo "🔄 時間が限られている場合は /note_article_standard をお試しください"
            # 高品質版のロジック実行
            create_premium_article "$ARGUMENTS"
            ;;
    esac
}
```

## 📝 実行フロー

1. **自動分析**: トピックの複雑性を分析
2. **推奨表示**: 最適な方式を提案
3. **自動実行**: 推奨方式で記事作成開始
4. **代替案提示**: 他の選択肢も案内

## 🎯 各レベルの実装

### Quick版実装
```bash
create_quick_article() {
    local topic="$1"
    echo "📝 Quick記事作成: $topic"
    
    # テンプレート自動選択
    select_template "$topic"
    
    # 基本構成生成
    generate_basic_structure "$topic"
    
    # 最小限品質チェック
    basic_quality_check
    
    echo "✅ 記事作成完了（docs/91.notes/）"
}
```

### Standard版実装
```bash
create_standard_article() {
    local topic="$1"
    echo "⚖️ Standard記事作成: $topic"
    
    # 要件分析
    analyze_requirements "$topic"
    
    # 構造化作成
    create_structured_content "$topic"
    
    # 標準品質ゲート
    standard_quality_check
    
    echo "✅ 記事作成完了（品質スコア: 75+点）"
}
```

### 高品質版実装
```bash
create_premium_article() {
    local topic="$1"
    echo "🏆 高品質記事作成: $topic"
    echo "⚠️ 完全版のプロセスを実行します（30-45分）"
    
    # 既存の完全版プロセス実行
    # （現在のnote_article.mdの内容）
    execute_full_competitive_development "$topic"
}
```

## 🎨 ユーザー体験の向上

### シンプルな使用方法
```bash
# これだけで最適な記事が作成される
/note_article_auto "tmuxを使った効率的な開発環境構築"

# 実行例:
# 📊 最適な記事作成方式を分析中...
# ⚖️ 推奨: Standard版（15-20分）- バランス重視
# ✅ Standard版で記事を作成します
# 📝 記事作成開始...
```

### 透明性の確保
- 判定理由の表示
- 代替選択肢の提示
- 予想所要時間の明示
- いつでも中断・変更可能

---

**利点**: ユーザーは複雑な選択をせずに、システムが最適な方式を自動選択。透明性も確保。