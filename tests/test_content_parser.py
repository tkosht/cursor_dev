"""ContentParserのテストモジュール。

このモジュールは、ContentParserクラスの各メソッドの動作を検証します。

必要性：
- HTML解析機能の検証
- 情報抽出の正確性確認
- エラーハンドリングの検証

十分性：
- 様々なHTML構造のテスト
- エッジケースの網羅
- 正規化処理の検証
"""

import pytest
from bs4 import BeautifulSoup
from app.content_parser import ContentParser

def test_init():
    """初期化の正常系をテストする。
    
    必要性：
    - 初期化処理の確認
    - 不要タグリストの検証
    
    十分性：
    - インスタンス生成の確認
    - 不要タグの完全性確認
    """
    parser = ContentParser()
    assert isinstance(parser, ContentParser)
    assert parser.unwanted_tags == {
        'script', 'style', 'iframe', 'form',
        'nav', 'header', 'footer', 'aside'
    }

def test_parse_html_empty():
    """空のHTML処理をテストする。
    
    必要性：
    - 入力検証の確認
    - エラーメッセージの検証
    
    十分性：
    - 空文字列での呼び出し
    - エラーメッセージの確認
    """
    parser = ContentParser()
    with pytest.raises(ValueError) as exc_info:
        parser.parse_html("")
    assert "HTMLが空です" in str(exc_info.value)

def test_parse_html_success():
    """HTML解析の成功ケースをテストする。
    
    必要性：
    - 正常系の動作確認
    - 抽出結果の検証
    
    十分性：
    - 全要素の抽出確認
    - 結果の形式検証
    """
    html = """
    <html>
        <head>
            <title>テストページ</title>
            <meta property="og:url" content="https://example.com">
            <meta property="article:published_time" content="2024-01-07">
        </head>
        <body>
            <article>
                <h1>メインタイトル</h1>
                <p>テストコンテンツ</p>
            </article>
            <script>alert('test');</script>
        </body>
    </html>
    """
    
    parser = ContentParser()
    result = parser.parse_html(html)
    
    assert isinstance(result, dict)
    assert result["title"] == "テストページ"
    assert "テストコンテンツ" in result["content"]
    assert result["date"] == "2024-01-07"
    assert result["url"] == "https://example.com"

def test_remove_unwanted_tags():
    """不要タグの削除をテストする。
    
    必要性：
    - タグ削除機能の確認
    - 本文抽出への影響確認
    
    十分性：
    - 全不要タグの削除確認
    - コンテンツ保持の確認
    """
    html = """
    <html>
        <body>
            <article>メインコンテンツ</article>
            <script>alert('test');</script>
            <style>.test{color:red;}</style>
            <nav>ナビゲーション</nav>
        </body>
    </html>
    """
    
    parser = ContentParser()
    soup = BeautifulSoup(html, 'html.parser')
    cleaned_soup = parser._remove_unwanted_tags(soup)
    
    assert cleaned_soup.find('script') is None
    assert cleaned_soup.find('style') is None
    assert cleaned_soup.find('nav') is None
    assert "メインコンテンツ" in cleaned_soup.get_text()

def test_extract_title_variations():
    """タイトル抽出の様々なパターンをテストする。
    
    必要性：
    - 異なるタイトル要素の処理確認
    - フォールバック動作の検証
    
    十分性：
    - title要素からの抽出
    - h1要素からの抽出
    - タイトルなしの場合の処理
    """
    parser = ContentParser()
    
    # title要素からの抽出
    html1 = "<html><head><title>テストタイトル</title></head></html>"
    soup1 = BeautifulSoup(html1, 'html.parser')
    assert parser._extract_title(soup1) == "テストタイトル"
    
    # h1要素からの抽出
    html2 = "<html><body><h1>H1タイトル</h1></body></html>"
    soup2 = BeautifulSoup(html2, 'html.parser')
    assert parser._extract_title(soup2) == "H1タイトル"
    
    # タイトルなしの場合
    html3 = "<html><body></body></html>"
    soup3 = BeautifulSoup(html3, 'html.parser')
    assert parser._extract_title(soup3) == "タイトルなし"

def test_extract_content_variations():
    """本文抽出の様々なパターンをテストする。
    
    必要性：
    - 異なる本文要素の処理確認
    - フォールバック動作の検証
    
    十分性：
    - article要素からの抽出
    - main要素からの抽出
    - div要素からの抽出
    """
    parser = ContentParser()
    
    # article要素からの抽出
    html1 = "<html><body><article>記事本文</article></body></html>"
    soup1 = BeautifulSoup(html1, 'html.parser')
    assert parser._extract_content(soup1) == "記事本文"
    
    # main要素からの抽出
    html2 = "<html><body><main>メインコンテンツ</main></body></html>"
    soup2 = BeautifulSoup(html2, 'html.parser')
    assert parser._extract_content(soup2) == "メインコンテンツ"
    
    # div要素からの抽出
    html3 = """
    <html><body>
        <div>短いテキスト</div>
        <div>とても長いテキストとても長いテキストとても長いテキスト</div>
    </body></html>
    """
    soup3 = BeautifulSoup(html3, 'html.parser')
    content = parser._extract_content(soup3)
    assert "とても長いテキスト" in content

def test_extract_date_variations():
    """日付抽出の様々なパターンをテストする。
    
    必要性：
    - 異なる日付要素の処理確認
    - フォールバック動作の検証
    
    十分性：
    - time要素からの抽出
    - meta要素からの抽出
    - 日付なしの場合の処理
    """
    parser = ContentParser()
    
    # time要素からの抽出
    html1 = '<html><body><time datetime="2024-01-07">2024年1月7日</time></body></html>'
    soup1 = BeautifulSoup(html1, 'html.parser')
    assert parser._extract_date(soup1) == "2024-01-07"
    
    # meta要素からの抽出
    html2 = '<html><head><meta property="article:published_time" content="2024-01-07"></head></html>'
    soup2 = BeautifulSoup(html2, 'html.parser')
    assert parser._extract_date(soup2) == "2024-01-07"
    
    # 日付なしの場合
    html3 = "<html><body></body></html>"
    soup3 = BeautifulSoup(html3, 'html.parser')
    assert parser._extract_date(soup3) is None

def test_extract_url_variations():
    """URL抽出の様々なパターンをテストする。
    
    必要性：
    - 異なるURL要素の処理確認
    - フォールバック動作の検証
    
    十分性：
    - canonical要素からの抽出
    - meta要素からの抽出
    - URLなしの場合の処理
    """
    parser = ContentParser()
    
    # canonical要素からの抽出
    html1 = '<html><head><link rel="canonical" href="https://example.com/page1"></head></html>'
    soup1 = BeautifulSoup(html1, 'html.parser')
    assert parser._extract_url(soup1) == "https://example.com/page1"
    
    # meta要素からの抽出
    html2 = '<html><head><meta property="og:url" content="https://example.com/page2"></head></html>'
    soup2 = BeautifulSoup(html2, 'html.parser')
    assert parser._extract_url(soup2) == "https://example.com/page2"
    
    # URLなしの場合
    html3 = "<html><body></body></html>"
    soup3 = BeautifulSoup(html3, 'html.parser')
    assert parser._extract_url(soup3) is None

def test_normalize_text():
    """テキスト正規化をテストする。
    
    必要性：
    - 正規化処理の確認
    - エッジケースの処理確認
    
    十分性：
    - 空白・改行の処理
    - 空文字列の処理
    - 複数行テキストの処理
    """
    parser = ContentParser()
    
    # 空文字列
    assert parser._normalize_text("") == ""
    
    # 空白と改行の処理
    text1 = "  テスト  \n  テキスト  "
    assert parser._normalize_text(text1) == "テスト\nテキスト"
    
    # 複数行の処理
    text2 = """
    
    1行目
      2行目
    
    3行目
    
    """
    assert parser._normalize_text(text2) == "1行目\n2行目\n3行目" 