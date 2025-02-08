"""ContentParserのテストモジュール。"""

import pytest

from app.content_parser import ContentParser
from app.exceptions import ContentParseError


@pytest.fixture
def content_parser():
    """ContentParserのインスタンスを生成するフィクスチャ。"""
    return ContentParser()


def test_parse_html_success(content_parser):
    """HTMLの解析が成功するケースをテストする。"""
    html = """
    <html>
        <head>
            <title>テストタイトル</title>
        </head>
        <body>
            <article>
                <h1>記事タイトル</h1>
                <p>これは本文です。</p>
                <time datetime="2025-01-11">2025年1月11日</time>
            </article>
        </body>
    </html>
    """
    result = content_parser.parse_content(html)
    assert result["title"] == "記事タイトル"
    assert result["content"] == "これは本文です。"
    assert result["date"] == "2025-01-11"


def test_parse_html_empty(content_parser):
    """空のHTMLを解析した場合のテストを行う。"""
    with pytest.raises(ContentParseError):
        content_parser.parse_content("")


def test_remove_unwanted_tags(content_parser):
    """不要なタグを削除する機能をテストする。"""
    html = """
    <article>
        <h1>タイトル</h1>
        <p>本文<script>alert('test');</script></p>
        <style>.test { color: red; }</style>
    </article>
    """
    result = content_parser.parse_content(html)
    assert "script" not in result["content"]
    assert "style" not in result["content"]


def test_extract_title_variations(content_parser):
    """タイトル抽出の様々なパターンをテストする。"""
    # h1タグからの抽出
    html1 = "<article><h1>タイトル1</h1></article>"
    result1 = content_parser.parse_content(html1)
    assert result1["title"] == "タイトル1"

    # titleタグからの抽出
    html2 = "<html><head><title>タイトル2</title></head></html>"
    result2 = content_parser.parse_content(html2)
    assert result2["title"] == "タイトル2"

    # メタタグからの抽出
    html3 = """
    <html>
        <head>
            <meta property="og:title" content="タイトル3">
        </head>
    </html>
    """
    result3 = content_parser.parse_content(html3)
    assert result3["title"] == "タイトル3"


def test_extract_content_variations(content_parser):
    """本文抽出の様々なパターンをテストする。"""
    # articleタグからの抽出
    html1 = "<article><p>本文1</p></article>"
    result1 = content_parser.parse_content(html1)
    assert result1["content"] == "本文1"

    # mainタグからの抽出
    html2 = "<main><p>本文2</p></main>"
    result2 = content_parser.parse_content(html2)
    assert result2["content"] == "本文2"

    # 最長テキストブロックからの抽出
    html3 = """
    <div>短いテキスト</div>
    <div>これは長いテキストブロックです。
    複数行にわたる本文を含んでいます。
    このブロックが本文として抽出されるべきです。</div>
    """
    result3 = content_parser.parse_content(html3)
    assert "長いテキストブロック" in result3["content"]


def test_extract_date_variations(content_parser):
    """日付抽出の様々なパターンをテストする。"""
    # timeタグからの抽出
    html1 = '<article><time datetime="2025-01-11">2025年1月11日</time></article>'
    result1 = content_parser.parse_content(html1)
    assert result1["date"] == "2025-01-11"

    # メタタグからの抽出
    html2 = """
    <html>
        <head>
            <meta property="article:published_time" content="2025-01-11">
        </head>
    </html>
    """
    result2 = content_parser.parse_content(html2)
    assert result2["date"] == "2025-01-11"

    # テキストからの抽出
    html3 = '<div>公開日: 2025年1月11日</div>'
    result3 = content_parser.parse_content(html3)
    assert result3["date"] == "2025-01-11"


def test_normalize_text(content_parser):
    """テキストの正規化をテストする。"""
    html = """
    <article>
        <p>これは  複数の   空白を   含む
        テキスト   です。</p>
        <p>これは
        改行を
        含むテキストです。</p>
    </article>
    """
    result = content_parser.parse_content(html)
    assert "これは 複数の 空白を 含む テキスト です。" in result["content"]
    assert "これは 改行を 含むテキストです。" in result["content"] 