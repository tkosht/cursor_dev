"""
ニュース情報モデルのテスト

このモジュールは、ニュース情報モデルの機能をテストします。
"""

from datetime import datetime, timezone

import pytest

from app.models.news import News


def test_create_news(session, sample_news):
    """ニュース情報の作成をテストします。"""
    assert sample_news.id is not None
    assert sample_news.title == "2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
    assert sample_news.source == "適時開示"
    assert sample_news.category == "決算情報"


def test_news_to_dict(sample_news):
    """ニュース情報モデルの辞書変換をテストします。"""
    data = sample_news.to_dict()
    assert data["title"] == "2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
    assert data["source"] == "適時開示"
    assert data["category"] == "決算情報"


def test_news_from_dict(session, sample_company):
    """辞書からのニュース情報モデル作成をテストします。"""
    data = {
        "company_id": sample_company.id,
        "title": "新製品発表のお知らせ",
        "content": "新製品XXXを発表いたしました。",
        "url": "https://example.com/news/001",
        "published_at": datetime(2024, 1, 5, 10, 0, tzinfo=timezone.utc),
        "source": "プレスリリース",
        "category": "製品情報"
    }
    news = News.from_dict(data)
    session.add(news)
    session.commit()

    assert news.id is not None
    assert news.title == "新製品発表のお知らせ"
    assert news.source == "プレスリリース"


def test_news_update(sample_news):
    """ニュース情報の更新をテストします。"""
    data = {
        "title": "【更新】2024年2月期 第3四半期決算短信〔IFRS〕（連結）",
        "content": "内容を更新しました。"
    }
    sample_news.update(data)

    assert sample_news.title == "【更新】2024年2月期 第3四半期決算短信〔IFRS〕（連結）"
    assert sample_news.content == "内容を更新しました。"
    # 更新されていないフィールドは元の値のまま
    assert sample_news.source == "適時開示"


def test_news_relationship(session, sample_news):
    """ニュース情報モデルのリレーションシップをテストします。"""
    company = sample_news.company
    assert company is not None
    assert company.name == "ニトリホールディングス"
    assert company.company_code == "9843"


def test_news_url_required(session, sample_company):
    """URLが必須であることをテストします。"""
    news = News(
        company_id=sample_company.id,
        title="テストニュース",
        published_at=datetime.now(timezone.utc),
        source="テスト"
    )
    session.add(news)
    
    with pytest.raises(Exception):  # SQLAlchemyの具体的な例外クラスは環境依存
        session.commit() 