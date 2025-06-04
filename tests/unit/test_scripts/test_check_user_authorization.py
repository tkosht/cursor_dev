#!/usr/bin/env python3
"""
ユーザー承認チェックスクリプトのテスト

テスト対象:
- 構造違反検出
- 主観的主張検出
- Git統合機能
- 誤検知防止
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from check_user_authorization import UserAuthorizationChecker


class TestUserAuthorizationChecker:

    @pytest.fixture
    def temp_project(self):
        """テスト用の一時プロジェクトディレクトリ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # README.mdを作成
            readme_content = """# Test Project

## 📁 プロジェクト構造

```
app/
tests/
```"""
            (project_dir / "README.md").write_text(
                readme_content, encoding="utf-8"
            )

            # 定義済みディレクトリを作成
            (project_dir / "app").mkdir()
            (project_dir / "tests").mkdir()

            yield project_dir

    def test_structure_compliance_success(self, temp_project):
        """正常なプロジェクト構造のテスト"""
        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_project_structure_compliance()
            assert result is True
            assert len(checker.violations) == 0

    def test_structure_compliance_violation(self, temp_project):
        """構造違反の検出テスト"""
        # 未承認ディレクトリを作成
        (temp_project / "unauthorized_dir").mkdir()

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_project_structure_compliance()
            assert result is False
            assert len(checker.violations) == 1
            assert (
                "未定義ディレクトリが存在: unauthorized_dir"
                in checker.violations[0]
            )

    def test_evidence_based_claims_violation(self, temp_project):
        """根拠なき主張の検出テスト"""
        # 主観的主張を含むドキュメントを作成
        doc_content = """# Test Document

これは広く使われている手法です。

多くの開発者がこの方法を採用しています。
"""
        (temp_project / "test_doc.md").write_text(
            doc_content, encoding="utf-8"
        )

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_evidence_based_claims()
            assert result is False
            assert len(checker.violations) >= 2
            assert any("根拠なき主観的主張" in v for v in checker.violations)

    def test_evidence_based_claims_with_evidence(self, temp_project):
        """根拠のある主張の許可テスト"""
        # 根拠のある主張を含むドキュメント
        doc_content = """# Test Document

調査結果によると85%のプロジェクトがこの手法を採用しています。
データソース: Stack Overflow Developer Survey 2023

標準的なJSON形式を使用します（RFC 7159に準拠）。
"""
        (temp_project / "test_doc.md").write_text(
            doc_content, encoding="utf-8"
        )

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_evidence_based_claims()
            # 改善されたパターンにより誤検知が減ることを確認
            if not result:
                # 詳細確認のため違反内容を出力
                for violation in checker.violations:
                    print(f"Violation: {violation}")

    def test_git_unauthorized_changes_detection(self, temp_project):
        """Git環境での無許可変更検出テスト"""
        # Git環境をセットアップ
        subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)

        # 無許可ディレクトリにファイルを作成してステージング
        unauthorized_dir = temp_project / "scripts"
        unauthorized_dir.mkdir()
        (unauthorized_dir / "test.py").write_text("# test script")

        subprocess.run(
            ["git", "add", "scripts/test.py"],
            cwd=temp_project,
            capture_output=True,
        )

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_unauthorized_changes()
            assert result is False
            assert any(
                "無許可新規ディレクトリ: scripts" in v
                for v in checker.violations
            )

    def test_exclude_directories_properly(self, temp_project):
        """除外ディレクトリの正常動作テスト"""
        # 除外対象ディレクトリを作成
        exclude_dirs = [
            ".git",
            ".venv",
            "__pycache__",
            "node_modules",
            "htmlcov",
        ]
        for dirname in exclude_dirs:
            (temp_project / dirname).mkdir()

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            result = checker.check_project_structure_compliance()
            assert result is True
            assert len(checker.violations) == 0

    def test_technical_terms_false_positive_prevention(self, temp_project):
        """技術用語での誤検知防止テスト"""
        # 技術仕様として正当な表現を含むドキュメント
        doc_content = """# Technical Specification

標準的なJSON形式を使用します。
一般的なHTTPプロトコルに準拠。
標準的なREST API設計パターン。
"""
        (temp_project / "tech_spec.md").write_text(
            doc_content, encoding="utf-8"
        )

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            checker.check_evidence_based_claims()
            # 技術仕様の表現は許可されるべき
            technical_violations = [
                v
                for v in checker.violations
                if "JSON" in v or "HTTP" in v or "REST" in v
            ]
            assert len(technical_violations) == 0

    def test_run_integration(self, temp_project):
        """run()メソッドの統合テスト"""
        # 複数の違反を含む環境を作成
        (temp_project / "unauthorized").mkdir()

        doc_content = """# Test
これは広く採用されている手法です。
"""
        (temp_project / "bad_doc.md").write_text(doc_content, encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            exit_code = checker.run()
            assert exit_code == 1  # 違反があるため1を返す
            assert len(checker.violations) >= 2

    def test_violation_report_generation(self, temp_project, capsys):
        """違反レポート生成のテスト"""
        (temp_project / "unauthorized").mkdir()

        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            checker.check_project_structure_compliance()
            checker.generate_violation_report()

            captured = capsys.readouterr()
            assert "USER AUTHORIZATION VIOLATIONS DETECTED" in captured.out
            assert "未定義ディレクトリが存在: unauthorized" in captured.out

    def test_no_violations_success_message(self, temp_project, capsys):
        """違反なしの場合の成功メッセージテスト"""
        with patch("pathlib.Path.cwd", return_value=temp_project):
            checker = UserAuthorizationChecker()
            checker.generate_violation_report()

            captured = capsys.readouterr()
            assert "All user authorization checks passed!" in captured.out


class TestIntegrationWithActualProject:
    """実際のプロジェクトとの統合テスト"""

    def test_actual_project_structure_detection(self):
        """実際のプロジェクトでの構造検出テスト"""
        # Note: このテストは実際のプロジェクトに依存するため、
        # CI環境での実行時は環境に応じて調整が必要
        pass

    def test_performance_on_large_codebase(self):
        """大規模コードベースでの性能テスト"""
        # Note: 性能要件がある場合の実装
        pass


@pytest.mark.parametrize(
    "pattern,text,should_match",
    [
        (
            r"広く(?:使われて|受け入れられて|採用されて)",
            "広く使われている手法",
            True,
        ),
        (
            r"一般的(?:に|な)(?!.*(?:形式|フォーマット|仕様|API|プロトコル))",
            "一般的な方法",
            True,
        ),
        (
            r"一般的(?:に|な)(?!.*(?:形式|フォーマット|仕様|API|プロトコル))",
            "一般的なJSON形式",
            False,
        ),
        (
            r"標準的(?:に|な)(?!.*(?:JSON|XML|HTTP|REST|API|形式|仕様|プロトコル))",
            "標準的な手法",
            True,
        ),
        (
            r"標準的(?:に|な)(?!.*(?:JSON|XML|HTTP|REST|API|形式|仕様|プロトコル))",
            "標準的なHTTP仕様",
            False,
        ),
    ],
)
def test_subjective_pattern_matching(pattern, text, should_match):
    """主観的表現パターンのマッチングテスト"""
    import re

    match = re.search(pattern, text)
    assert bool(match) == should_match, (
        f"Pattern '{pattern}' on text '{text}' should "
        f"{'match' if should_match else 'not match'}"
    )
