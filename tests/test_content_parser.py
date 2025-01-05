"""ContentParserのテストモジュール。"""

import pytest
from bs4 import BeautifulSoup
from app.content_parser import ContentParser

@pytest.fixture
def parser():
    """ContentParserのインスタンスを生成するフィクスチャ。"""
    return ContentParser()

def test_parse_html_success(parser):
    """parse_html()が正常にHTMLを解析できることをテスト。"""
    html = """
    <html>
        <head>
            <title>テストページ</title>
        </head>
        <body>
            <article>
                <h1>メインタイトル</h1>
                <time datetime="2025-01-05">2025年1月5日</time>
                <p>これは本文です。</p>
            </article>
            <script>alert('test');</script>
        </body>
    </html>
    """
    result = parser.parse_html(html)
    assert result["title"] == "テストページ"
    assert "これは本文です。" in result["content"]
    assert result["date"] == "2025-01-05"

def test_parse_html_empty(parser):
    """parse_html()が空のHTMLを適切に処理できることをテスト。"""
    with pytest.raises(ValueError) as exc_info:
        parser.parse_html("")
    assert "HTMLが空です" in str(exc_info.value)

def test_remove_unwanted_tags(parser):
    """_remove_unwanted_tags()が不要なタグを適切に削除できることをテスト。"""
    html = """
    <div>
        <script>test();</script>
        <p>必要なコンテンツ</p>
        <style>.test{}</style>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    cleaned = parser._remove_unwanted_tags(soup)
    assert "test();" not in cleaned.get_text()
    assert "必要なコンテンツ" in cleaned.get_text()

def test_extract_title_with_title_tag(parser):
    """_extract_title()がtitleタグから適切にタイトルを抽出できることをテスト。"""
    html = "<html><head><title>テストタイトル</title></head></html>"
    soup = BeautifulSoup(html, 'html.parser')
    assert parser._extract_title(soup) == "テストタイトル"

def test_extract_title_with_h1(parser):
    """_extract_title()がh1タグから適切にタイトルを抽出できることをテスト。"""
    html = "<html><body><h1>H1タイトル</h1></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    assert parser._extract_title(soup) == "H1タイトル"

def test_extract_title_no_title(parser):
    """_extract_title()がタイトルが見つからない場合を適切に処理できることをテスト。"""
    html = "<html><body><p>本文のみ</p></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    assert parser._extract_title(soup) == "タイトルなし"

def test_extract_content_with_article(parser):
    """_extract_content()がarticleタグから適切に本文を抽出できることをテスト。"""
    html = """
    <html><body>
        <nav>ナビゲーション</nav>
        <article>記事の本文</article>
        <footer>フッター</footer>
    </body></html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    content = parser._extract_content(soup)
    assert "記事の本文" in content
    assert "ナビゲーション" not in content
    assert "フッター" not in content

def test_extract_date_with_time(parser):
    """_extract_date()がtime要素から適切に日付を抽出できることをテスト。"""
    html = '<html><body><time datetime="2025-01-05">2025年1月5日</time></body></html>'
    soup = BeautifulSoup(html, 'html.parser')
    assert parser._extract_date(soup) == "2025-01-05"

def test_extract_date_with_meta(parser):
    """_extract_date()がmeta要素から適切に日付を抽出できることをテスト。"""
    html = """
    <html><head>
        <meta property="article:published_time" content="2025-01-05T12:00:00">
    </head></html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    assert parser._extract_date(soup) == "2025-01-05T12:00:00"

def test_normalize_text(parser):
    """_normalize_text()が適切にテキストを正規化できることをテスト。"""
    text = "  line1  \n\n  line2  \n  line3  "
    normalized = parser._normalize_text(text)
    assert normalized == "line1\nline2\nline3"

def test_normalize_text_empty(parser):
    """_normalize_text()が空のテキストを適切に処理できることをテスト。"""
    assert parser._normalize_text("") == ""
    assert parser._normalize_text(None) == "" 