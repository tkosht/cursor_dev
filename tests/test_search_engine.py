"""SearchEngineのテスト"""

import os

import pytest

from app.search_engine import SearchEngine, SearchEngineError


@pytest.fixture
def index_dir(tmp_path):
    """一時的なインデックスディレクトリを作成"""
    return str(tmp_path / "search_index")


@pytest.fixture
def engine(index_dir):
    """テスト用のSearchEngineインスタンス"""
    return SearchEngine(index_dir=index_dir)


@pytest.fixture
def sample_bookmarks():
    """サンプルブックマークデータ"""
    return [
        {
            "id": "1",
            "url": "https://twitter.com/user/status/1",
            "text": "Pythonプログラミングが楽しい",
            "created_at": "1234567890",
        },
        {
            "id": "2",
            "url": "https://twitter.com/user/status/2",
            "text": "機械学習の最新論文を読んだ",
            "created_at": "1234567891",
        },
        {
            "id": "3",
            "url": "https://twitter.com/user/status/3",
            "text": "今日は晴れていい天気",
            "created_at": "1234567892",
        },
    ]


def test_init_creates_empty_index(index_dir):
    """初期化時に空のインデックスが作成されることを確認"""
    engine = SearchEngine(index_dir=index_dir)
    assert os.path.exists(os.path.join(index_dir, 'faiss.index'))
    assert os.path.exists(os.path.join(index_dir, 'bookmarks.npy'))
    assert engine.get_total_bookmarks() == 0


def test_add_bookmarks(engine, sample_bookmarks):
    """ブックマークの追加が正常に動作することを確認"""
    engine.add_bookmarks(sample_bookmarks)
    assert engine.get_total_bookmarks() == 3
    
    # インデックスファイルが保存されていることを確認
    assert os.path.exists(os.path.join(engine.index_dir, 'faiss.index'))
    assert os.path.exists(os.path.join(engine.index_dir, 'bookmarks.npy'))


def test_search_with_no_bookmarks(engine):
    """ブックマークが無い状態での検索が正常に動作することを確認"""
    results = engine.search("Python")
    assert isinstance(results, list)
    assert len(results) == 0


def test_search_returns_relevant_results(engine, sample_bookmarks):
    """関連する検索結果が返されることを確認"""
    engine.add_bookmarks(sample_bookmarks)
    
    # Pythonに関する検索
    results = engine.search("Python programming")
    assert len(results) > 0
    assert isinstance(results[0], tuple)
    bookmark, score = results[0]
    assert "Python" in bookmark["text"]
    assert isinstance(score, float)
    
    # 機械学習に関する検索
    results = engine.search("machine learning")
    assert len(results) > 0
    bookmark, score = results[0]
    assert "機械学習" in bookmark["text"]


def test_search_with_top_k(engine, sample_bookmarks):
    """top_kパラメータが正常に動作することを確認"""
    engine.add_bookmarks(sample_bookmarks)
    results = engine.search("プログラミング", top_k=2)
    assert len(results) == 2


def test_clear_index(engine, sample_bookmarks):
    """インデックスのクリアが正常に動作することを確認"""
    engine.add_bookmarks(sample_bookmarks)
    assert engine.get_total_bookmarks() > 0
    
    engine.clear()
    assert engine.get_total_bookmarks() == 0


def test_persistence(index_dir, sample_bookmarks):
    """インデックスの永続化が正常に動作することを確認"""
    # 最初のインスタンスでデータを追加
    engine1 = SearchEngine(index_dir=index_dir)
    engine1.add_bookmarks(sample_bookmarks)
    total_bookmarks = engine1.get_total_bookmarks()
    
    # 新しいインスタンスを作成し、データが読み込まれることを確認
    engine2 = SearchEngine(index_dir=index_dir)
    assert engine2.get_total_bookmarks() == total_bookmarks
    
    # 検索も正常に動作することを確認
    results = engine2.search("Python")
    assert len(results) > 0


def test_invalid_index_dir():
    """無効なインデックスディレクトリでのエラーハンドリングを確認"""
    with pytest.raises(SearchEngineError) as exc_info:
        SearchEngine(index_dir="/invalid/directory/that/does/not/exist")
    assert "SearchEngineの初期化に失敗" in str(exc_info.value) 
