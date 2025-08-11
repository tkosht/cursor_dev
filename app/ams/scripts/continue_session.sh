#!/bin/bash

# AMS プロジェクト セッション継続スクリプト
# 前回セッション: 2025-08-10 テストレビュー完了

echo "================================================"
echo "AMS プロジェクト - セッション継続"
echo "================================================"
echo ""

# セッション状態確認
echo "📌 セッション状態:"
echo "-------------------"
if [ -f "SESSION_STATE.md" ]; then
    head -20 SESSION_STATE.md | grep -E "^###|^✅|^🔴"
else
    echo "⚠️  SESSION_STATE.md が見つかりません"
fi
echo ""

# アクションアイテム確認
echo "📋 Priority 1 アクションアイテム:"
echo "--------------------------------"
if [ -f "docs/ams_test_review_action_items.md" ]; then
    grep -A 5 "## 🔴 Priority 1:" docs/ams_test_review_action_items.md | head -10
else
    echo "⚠️  アクションアイテムファイルが見つかりません"
fi
echo ""

# モック使用箇所の確認
echo "🔍 現在のモック使用状況:"
echo "------------------------"
echo "検索中..."
MOCK_COUNT=$(grep -r "Mock\|patch" tests/ 2>/dev/null | wc -l)
echo "モック使用箇所: $MOCK_COUNT 件"
if [ $MOCK_COUNT -gt 0 ]; then
    echo ""
    echo "詳細（最初の5件）:"
    grep -r "Mock\|patch" tests/ 2>/dev/null | head -5
fi
echo ""

# 次のステップ案内
echo "🚀 次のステップ:"
echo "---------------"
echo "1. アクションアイテム確認:"
echo "   cat docs/ams_test_review_action_items.md"
echo ""
echo "2. 詳細レビュー確認:"
echo "   cat docs/ams_test_review_critical_issues_report.md"
echo ""
echo "3. モック削除作業開始:"
echo "   vim tests/unit/test_aggregator.py"
echo ""
echo "4. テスト実行:"
echo "   pytest tests/ -v"
echo ""
echo "================================================"
echo "準備完了！Priority 1 タスクから開始してください。"
echo "================================================"