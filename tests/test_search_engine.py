"""SearchEngineのテスト"""

import os
import time
from unittest.mock import patch

import pytest
import torch

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


@pytest.fixture
def large_sample_bookmarks():
    """パフォーマンステスト用の大量サンプルデータ"""
    base_texts = [
        "Pythonプログラミング",
        "機械学習",
        "データサイエンス",
        "ウェブ開発",
        "クラウドコンピューティング"
    ]
    bookmarks = []
    for i in range(1000):  # 1000件のブックマーク
        text = f"{base_texts[i % len(base_texts)]}に関する投稿 {i}"
        bookmarks.append({
            "id": str(i),
            "url": f"https://twitter.com/user/status/{i}",
            "text": text,
            "created_at": str(1234567890 + i)
        })
    return bookmarks


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


# GPU関連のテスト

@pytest.mark.skipif(not torch.cuda.is_available(), reason="GPUが利用できない環境")
def test_gpu_initialization(index_dir):
    """GPUが利用可能な場合のGPU初期化を確認"""
    engine = SearchEngine(index_dir=index_dir, use_gpu=True)
    assert engine.use_gpu is True
    assert engine.model.device.type == 'cuda'


@pytest.mark.skipif(not torch.cuda.is_available(), reason="GPUが利用できない環境")
def test_gpu_search(index_dir, sample_bookmarks):
    """GPUでの検索が正常に動作することを確認"""
    engine = SearchEngine(index_dir=index_dir, use_gpu=True)
    engine.add_bookmarks(sample_bookmarks)
    results = engine.search("Python")
    assert len(results) > 0


def test_gpu_fallback(index_dir):
    """GPU指定時にGPUが利用できない場合のフォールバックを確認"""
    with patch('torch.cuda.is_available', return_value=False):
        engine = SearchEngine(index_dir=index_dir, use_gpu=True)
        assert engine.use_gpu is False
        assert engine.model.device.type == 'cpu'


# エラーケースのテスト

def test_add_empty_bookmarks(engine):
    """空のブックマークリスト追加時の動作を確認"""
    engine.add_bookmarks([])
    assert engine.get_total_bookmarks() == 0


def test_add_invalid_bookmarks(engine):
    """無効なブックマークデータ追加時のエラーハンドリングを確認"""
    invalid_bookmarks = [{"invalid": "data"}]
    with pytest.raises(SearchEngineError) as exc_info:
        engine.add_bookmarks(invalid_bookmarks)
    assert "ブックマークの追加に失敗" in str(exc_info.value)


def test_save_index_error(engine, sample_bookmarks):
    """インデックス保存時のエラーハンドリングを確認"""
    engine.add_bookmarks(sample_bookmarks)
    with patch('faiss.write_index', side_effect=Exception("保存エラー")):
        with pytest.raises(SearchEngineError) as exc_info:
            engine._save_index()
        assert "インデックスの保存に失敗" in str(exc_info.value)


def test_search_error(engine, sample_bookmarks):
    """検索時のエラーハンドリングを確認"""
    engine.add_bookmarks(sample_bookmarks)
    with patch.object(engine.index, 'search', side_effect=Exception("検索エラー")):
        with pytest.raises(SearchEngineError) as exc_info:
            engine.search("Python")
        assert "検索に失敗" in str(exc_info.value)


# パフォーマンステスト

def test_search_performance(engine, large_sample_bookmarks):
    """検索のパフォーマンスを確認"""
    engine.add_bookmarks(large_sample_bookmarks)
    
    start_time = time.time()
    results = engine.search("Python", top_k=10)
    end_time = time.time()
    
    search_time = end_time - start_time
    assert search_time < 1.0  # 検索は1秒以内に完了すべき
    assert len(results) == 10


def test_add_bookmarks_performance(engine, large_sample_bookmarks):
    """大量のブックマーク追加時のパフォーマンスを確認"""
    start_time = time.time()
    engine.add_bookmarks(large_sample_bookmarks)
    end_time = time.time()
    
    add_time = end_time - start_time
    assert add_time < 30.0  # 1000件の追加は30秒以内に完了すべき
    assert engine.get_total_bookmarks() == len(large_sample_bookmarks)


def test_memory_usage(engine, large_sample_bookmarks):
    """メモリ使用量を確認"""
    import psutil
    process = psutil.Process()
    
    initial_memory = process.memory_info().rss
    engine.add_bookmarks(large_sample_bookmarks)
    final_memory = process.memory_info().rss
    
    memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB単位
    assert memory_increase < 2000  # メモリ増加は2GB以内に抑えるべき 


def test_load_corrupted_index(index_dir, sample_bookmarks):
    """破損したインデックスファイルの読み込み時のエラーハンドリングを確認"""
    # 正常なインデックスを作成
    engine = SearchEngine(index_dir=index_dir)
    engine.add_bookmarks(sample_bookmarks)
    
    # インデックスファイルを破損させる
    with open(os.path.join(index_dir, 'faiss.index'), 'w') as f:
        f.write('corrupted data')
    
    # 破損したインデックスの読み込みを試行
    with pytest.raises(SearchEngineError) as exc_info:
        SearchEngine(index_dir=index_dir)
    assert "SearchEngineの初期化に失敗" in str(exc_info.value)


def test_load_corrupted_bookmarks(index_dir, sample_bookmarks):
    """破損したブックマークファイルの読み込み時のエラーハンドリングを確認"""
    # 正常なインデックスを作成
    engine = SearchEngine(index_dir=index_dir)
    engine.add_bookmarks(sample_bookmarks)
    
    # ブックマークファイルを破損させる
    with open(os.path.join(index_dir, 'bookmarks.npy'), 'w') as f:
        f.write('corrupted data')
    
    # 破損したブックマークの読み込みを試行
    with pytest.raises(SearchEngineError) as exc_info:
        SearchEngine(index_dir=index_dir)
    assert "SearchEngineの初期化に失敗" in str(exc_info.value)


def test_long_text_handling(engine):
    """非常に長いテキストの処理を確認"""
    long_text = "あ" * 10000  # 1万文字の長いテキスト
    bookmarks = [{
        "id": "1",
        "url": "https://twitter.com/user/status/1",
        "text": long_text,
        "created_at": "1234567890"
    }]
    
    engine.add_bookmarks(bookmarks)
    results = engine.search(long_text[:100])  # 最初の100文字で検索
    assert len(results) > 0
    assert results[0][0]["text"] == long_text


def test_special_characters(engine):
    """特殊文字を含むテキストの処理を確認"""
    special_chars = "!@#$%^&*()_+-=[]{}|;:'\",.<>?/~`"
    bookmarks = [{
        "id": "1",
        "url": "https://twitter.com/user/status/1",
        "text": f"特殊文字テスト {special_chars}",
        "created_at": "1234567890"
    }]
    
    engine.add_bookmarks(bookmarks)
    results = engine.search(special_chars)
    assert len(results) > 0
    assert special_chars in results[0][0]["text"]


def test_empty_text(engine):
    """空のテキストの処理を確認"""
    bookmarks = [{
        "id": "1",
        "url": "https://twitter.com/user/status/1",
        "text": "",
        "created_at": "1234567890"
    }]
    
    engine.add_bookmarks(bookmarks)
    results = engine.search("")
    assert isinstance(results, list)


def test_large_top_k(engine, sample_bookmarks):
    """極端に大きなtop_k値の処理を確認"""
    engine.add_bookmarks(sample_bookmarks)
    results = engine.search("Python", top_k=1000)
    assert len(results) == len(sample_bookmarks)  # 利用可能な全ブックマークが返される


@pytest.mark.skipif(not torch.cuda.is_available(), reason="GPUが利用できない環境")
def test_gpu_memory_management(index_dir):
    """GPUメモリ管理の確認"""
    import gc

    # 初期メモリ使用量を記録
    torch.cuda.empty_cache()
    gc.collect()
    initial_memory = torch.cuda.memory_allocated()
    
    # GPUエンジンを作成して使用
    engine = SearchEngine(index_dir=index_dir, use_gpu=True)
    used_memory = torch.cuda.memory_allocated()
    assert used_memory > initial_memory  # メモリ使用量が増加していることを確認
    
    # エンジンを削除してメモリをクリア
    del engine
    torch.cuda.empty_cache()
    gc.collect()
    final_memory = torch.cuda.memory_allocated()
    assert final_memory < used_memory  # メモリが解放されていることを確認


def test_gpu_cpu_switching(index_dir, sample_bookmarks):
    """GPU/CPU切り替え時の動作を確認"""
    # GPUエンジンを作成
    engine_gpu = SearchEngine(index_dir=index_dir, use_gpu=True)
    engine_gpu.add_bookmarks(sample_bookmarks)
    gpu_results = engine_gpu.search("Python")
    
    # 同じインデックスをCPUで読み込み
    engine_cpu = SearchEngine(index_dir=index_dir, use_gpu=False)
    cpu_results = engine_cpu.search("Python")
    
    # 結果が一致することを確認（浮動小数点の誤差を考慮）
    assert len(gpu_results) == len(cpu_results)
    for (gpu_bookmark, gpu_score), (cpu_bookmark, cpu_score) in zip(gpu_results, cpu_results):
        assert gpu_bookmark == cpu_bookmark
        assert abs(gpu_score - cpu_score) < 1e-5  # 許容誤差 