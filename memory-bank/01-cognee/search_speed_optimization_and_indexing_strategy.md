# Cognee検索速度向上とインデックス戦略設計書

**作成日**: 2025-06-16  
**チーム**: 検索最適化エンジニア、データベースアーキテクト、メタデータスペシャリスト  
**目的**: Cogneeの検索速度を劇的に向上させる統合的な戦略設計

## エグゼクティブサマリー

本文書は、Cogneeの検索速度向上とインデックス戦略について、3つの専門家視点から統合的な設計を提案します。段階的検索戦略、高度なメタデータインデックス構造、検索タイプ別最適化、そして登録時のメタデータ付与戦略を通じて、検索速度80%短縮と情報アクセス効率70%向上を実現します。

## 1. 検索最適化エンジニアの視点：段階的検索戦略

### 1.1 高速プレフィルタリング層（L1キャッシュ）

#### 設計思想
- **応答時間**: 0.1-0.5秒
- **キャッシュサイズ**: 最大100MB（頻出クエリTop 1000）
- **ヒット率目標**: 40-50%

#### 実装詳細
```python
class L1PreFilterCache:
    def __init__(self):
        self.cache = {}  # {query_hash: (result, timestamp, access_count)}
        self.max_size = 100 * 1024 * 1024  # 100MB
        self.ttl = 3600  # 1時間
        
    def get(self, query: str, search_type: str) -> Optional[SearchResult]:
        key = self._hash_key(query, search_type)
        if key in self.cache:
            result, timestamp, count = self.cache[key]
            if time.time() - timestamp < self.ttl:
                self.cache[key] = (result, timestamp, count + 1)
                return result
        return None
        
    def _hash_key(self, query: str, search_type: str) -> str:
        return hashlib.sha256(f"{query}:{search_type}".encode()).hexdigest()
```

### 1.2 段階的絞り込み検索（3段階アプローチ）

#### Phase 1: メタデータインデックス検索（1-3秒）
```python
async def phase1_metadata_search(query: str) -> List[DocumentMetadata]:
    """
    高速メタデータ検索
    - カテゴリマッチング
    - タグベース検索
    - ファイル名・パス検索
    """
    results = []
    
    # カテゴリ検索（事前計算済みインデックス）
    category_matches = await search_category_index(query)
    
    # タグ検索（転置インデックス）
    tag_matches = await search_tag_inverted_index(query)
    
    # ファイルパス検索（Trie構造）
    path_matches = await search_path_trie(query)
    
    return merge_and_rank(category_matches, tag_matches, path_matches)
```

#### Phase 2: セマンティック検索（5-10秒）
```python
async def phase2_semantic_search(
    query: str, 
    metadata_results: List[DocumentMetadata]
) -> List[SemanticMatch]:
    """
    ベクトル類似度検索
    - 事前計算済みエンベディング活用
    - コサイン類似度計算
    - 上位K件抽出
    """
    query_embedding = await get_embedding(query)
    
    # metadata_resultsから対象ドキュメントのエンベディングを取得
    doc_embeddings = await batch_get_embeddings(
        [m.doc_id for m in metadata_results]
    )
    
    # 類似度計算（GPU活用可能）
    similarities = compute_cosine_similarity(query_embedding, doc_embeddings)
    
    return get_top_k_matches(similarities, k=20)
```

#### Phase 3: 詳細コンテンツ検索（10-20秒、必要時のみ）
```python
async def phase3_deep_content_search(
    query: str,
    semantic_matches: List[SemanticMatch]
) -> List[DetailedResult]:
    """
    フルテキスト検索・グラフトラバーサル
    - Neo4jグラフ探索
    - PostgreSQLフルテキスト検索
    - 関係性分析
    """
    # グラフベース探索
    graph_results = await neo4j_graph_search(
        start_nodes=[m.node_id for m in semantic_matches],
        max_depth=3
    )
    
    # フルテキスト検索
    text_results = await postgres_full_text_search(
        query,
        doc_ids=[m.doc_id for m in semantic_matches]
    )
    
    return merge_graph_and_text_results(graph_results, text_results)
```

### 1.3 キャッシュ戦略の階層化

#### L1キャッシュ（メモリ内）
- **対象**: 頻出クエリ結果
- **サイズ**: 100MB
- **TTL**: 1時間
- **ヒット率**: 40-50%

#### L2キャッシュ（Redis）
- **対象**: セマンティック検索結果
- **サイズ**: 1GB
- **TTL**: 24時間
- **ヒット率**: 20-30%

#### L3キャッシュ（PostgreSQL）
- **対象**: 計算コストの高い結果
- **サイズ**: 10GB
- **TTL**: 7日間
- **ヒット率**: 10-15%

## 2. データベースアーキテクトの視点：インデックス構造設計

### 2.1 多層インデックスアーキテクチャ

#### プライマリインデックス（PostgreSQL）
```sql
-- ドキュメントメタデータインデックス
CREATE INDEX idx_documents_metadata ON documents 
USING GIN (
    to_tsvector('english', name || ' ' || description) || 
    array_to_tsvector(tags)
);

-- カテゴリ階層インデックス
CREATE INDEX idx_category_hierarchy ON documents 
USING btree (category_level1, category_level2, category_level3);

-- 時系列インデックス
CREATE INDEX idx_documents_timeline ON documents 
USING btree (created_at DESC, updated_at DESC);

-- 優先度スコアインデックス
CREATE INDEX idx_priority_score ON documents 
USING btree (priority_score DESC);
```

#### セカンダリインデックス（Neo4j）
```cypher
// カテゴリノードインデックス
CREATE INDEX category_name_index FOR (c:Category) ON (c.name);
CREATE INDEX category_level_index FOR (c:Category) ON (c.level);

// ドキュメントノードインデックス
CREATE INDEX document_name_index FOR (d:Document) ON (d.name);
CREATE INDEX document_hash_index FOR (d:Document) ON (d.content_hash);

// 関係性インデックス
CREATE INDEX rel_weight_index FOR ()-[r:RELATES_TO]-() ON (r.weight);
```

### 2.2 転置インデックス構造（高速キーワード検索）

```python
class InvertedIndex:
    """
    高速キーワード検索用転置インデックス
    """
    def __init__(self):
        self.index = {}  # {term: {doc_id: [positions]}}
        self.doc_lengths = {}  # {doc_id: length}
        self.term_frequencies = {}  # {term: frequency}
        
    def add_document(self, doc_id: str, content: str):
        tokens = self.tokenize(content)
        self.doc_lengths[doc_id] = len(tokens)
        
        for position, token in enumerate(tokens):
            if token not in self.index:
                self.index[token] = {}
                self.term_frequencies[token] = 0
                
            if doc_id not in self.index[token]:
                self.index[token][doc_id] = []
                
            self.index[token][doc_id].append(position)
            self.term_frequencies[token] += 1
            
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """BM25スコアリングによる検索"""
        query_tokens = self.tokenize(query)
        scores = {}
        
        for token in query_tokens:
            if token in self.index:
                idf = self._calculate_idf(token)
                
                for doc_id, positions in self.index[token].items():
                    tf = len(positions) / self.doc_lengths[doc_id]
                    bm25_score = self._bm25(tf, idf, self.doc_lengths[doc_id])
                    
                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += bm25_score
                    
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
```

### 2.3 階層的ブルームフィルタ（存在確認の高速化）

```python
class HierarchicalBloomFilter:
    """
    階層的ブルームフィルタによる存在確認の高速化
    """
    def __init__(self):
        self.category_filter = BloomFilter(capacity=10000, error_rate=0.001)
        self.tag_filter = BloomFilter(capacity=50000, error_rate=0.001)
        self.content_filter = BloomFilter(capacity=100000, error_rate=0.001)
        
    def add(self, doc: Document):
        # カテゴリレベル
        self.category_filter.add(doc.category)
        
        # タグレベル
        for tag in doc.tags:
            self.tag_filter.add(tag)
            
        # コンテンツレベル
        for keyword in doc.extract_keywords():
            self.content_filter.add(keyword)
            
    def might_contain(self, query: str) -> bool:
        """クエリが含まれる可能性があるかを高速判定"""
        tokens = tokenize(query)
        
        for token in tokens:
            if (token in self.category_filter or 
                token in self.tag_filter or 
                token in self.content_filter):
                return True
                
        return False
```

## 3. メタデータスペシャリストの視点：コンテキスト情報体系化

### 3.1 標準化メタデータスキーマ

```python
@dataclass
class StandardizedMetadata:
    """標準化されたメタデータ構造"""
    # 基本情報
    id: str
    name: str
    path: str
    content_hash: str
    
    # カテゴリ分類（3階層）
    category_l1: str  # 例: "00-core", "01-cognee"
    category_l2: str  # 例: "mandatory", "optional"
    category_l3: str  # 例: "rules", "patterns"
    
    # タグ・キーワード
    tags: List[str]  # 自動生成 + 手動追加
    keywords: List[str]  # TF-IDF抽出
    entities: List[str]  # NER抽出
    
    # 背景・前提条件
    context: Dict[str, Any] = field(default_factory=dict)
    prerequisites: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # 優先度・重要度
    priority: int = 1  # 1-5のスケール
    importance_score: float = 0.0  # 0.0-1.0
    access_frequency: int = 0
    
    # 時系列情報
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime
    
    # 関係性情報
    related_docs: List[str] = field(default_factory=list)
    parent_doc: Optional[str] = None
    child_docs: List[str] = field(default_factory=list)
```

### 3.2 自動メタデータ生成パイプライン

```python
class MetadataGenerationPipeline:
    """
    登録時の自動メタデータ生成
    """
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.keyword_extractor = KeyBERT()
        self.classifier = CategoryClassifier()
        
    async def generate_metadata(self, file_path: str, content: str) -> StandardizedMetadata:
        # 基本情報抽出
        metadata = StandardizedMetadata(
            id=str(uuid.uuid4()),
            name=os.path.basename(file_path),
            path=file_path,
            content_hash=hashlib.sha256(content.encode()).hexdigest(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        # カテゴリ分類
        categories = self._extract_categories_from_path(file_path)
        metadata.category_l1 = categories.get('l1', 'uncategorized')
        metadata.category_l2 = categories.get('l2', 'general')
        metadata.category_l3 = categories.get('l3', 'misc')
        
        # 自動タグ生成
        metadata.tags = await self._generate_tags(content)
        
        # キーワード抽出
        metadata.keywords = self.keyword_extractor.extract_keywords(
            content, 
            keyphrase_ngram_range=(1, 3), 
            stop_words='english',
            top_n=20
        )
        
        # エンティティ抽出
        doc = self.nlp(content[:10000])  # 最初の10000文字で分析
        metadata.entities = list(set([ent.text for ent in doc.ents]))
        
        # 優先度スコアリング
        metadata.priority = self._calculate_priority(file_path, content)
        metadata.importance_score = self._calculate_importance(metadata)
        
        # 関連ドキュメント推定
        metadata.related_docs = await self._find_related_docs(metadata)
        
        return metadata
```

### 3.3 コンテキスト情報の階層化

```python
class ContextHierarchy:
    """
    コンテキスト情報の階層的管理
    """
    def __init__(self):
        self.global_context = {}  # プロジェクト全体のコンテキスト
        self.category_context = {}  # カテゴリ別コンテキスト
        self.document_context = {}  # 個別ドキュメントコンテキスト
        
    def build_context_tree(self, documents: List[Document]):
        """コンテキストツリーの構築"""
        # グローバルコンテキスト
        self.global_context = {
            'project': 'A2A Protocol Investigation',
            'team': 'AI Development Team',
            'phase': 'Knowledge Management',
            'constraints': ['TDD', 'Security', 'Quality']
        }
        
        # カテゴリ別コンテキスト
        for doc in documents:
            category = doc.metadata.category_l1
            if category not in self.category_context:
                self.category_context[category] = {
                    'purpose': self._infer_category_purpose(category),
                    'dependencies': [],
                    'rules': []
                }
                
        # ドキュメント別コンテキスト
        for doc in documents:
            self.document_context[doc.id] = {
                'purpose': doc.metadata.context.get('purpose', ''),
                'prerequisites': doc.metadata.prerequisites,
                'usage': doc.metadata.context.get('usage', []),
                'examples': doc.metadata.context.get('examples', [])
            }
```

## 4. 統合的な高速検索システム設計

### 4.1 検索タイプ別最適化戦略

#### GRAPH_COMPLETION最適化
```python
class GraphCompletionOptimizer:
    def __init__(self):
        self.subgraph_cache = {}  # 事前計算済みサブグラフ
        self.path_cache = {}  # 頻出パスのキャッシュ
        
    async def optimize_graph_search(self, query: str):
        # 1. キーワードからスタートノード特定（高速）
        start_nodes = await self.find_start_nodes(query)
        
        # 2. 事前計算済みサブグラフ確認
        cached_subgraph = self.check_subgraph_cache(start_nodes)
        if cached_subgraph:
            return cached_subgraph
            
        # 3. 段階的グラフ探索
        results = await self.progressive_graph_search(
            start_nodes,
            max_depth=3,
            time_limit=5.0  # 5秒制限
        )
        
        return results
```

#### RAG_COMPLETION最適化
```python
class RAGCompletionOptimizer:
    def __init__(self):
        self.chunk_index = {}  # チャンクの事前インデックス
        self.relevance_cache = {}  # 関連性スコアキャッシュ
        
    async def optimize_rag_search(self, query: str):
        # 1. 高速チャンク検索（転置インデックス活用）
        relevant_chunks = await self.fast_chunk_retrieval(query)
        
        # 2. リランキング（軽量モデル使用）
        reranked_chunks = await self.lightweight_rerank(
            query, 
            relevant_chunks,
            top_k=10
        )
        
        # 3. コンテキスト生成（並列処理）
        context = await self.parallel_context_generation(reranked_chunks)
        
        return context
```

#### INSIGHTS最適化（関係性の事前計算）
```python
class InsightsOptimizer:
    def __init__(self):
        self.relationship_index = {}  # 関係性の事前計算インデックス
        self.pattern_cache = {}  # パターンキャッシュ
        
    async def precompute_relationships(self):
        """バッチ処理で関係性を事前計算"""
        # エンティティ間の関係性スコア計算
        entities = await self.get_all_entities()
        
        for e1, e2 in itertools.combinations(entities, 2):
            score = await self.calculate_relationship_score(e1, e2)
            if score > 0.5:  # 閾値以上のみ保存
                self.relationship_index[(e1.id, e2.id)] = {
                    'score': score,
                    'type': self.infer_relationship_type(e1, e2),
                    'evidence': self.extract_evidence(e1, e2)
                }
```

### 4.2 Cognee登録時のメタデータ付与戦略

```python
class CogneeMetadataEnricher:
    """
    Cognee登録時の自動メタデータ付与
    """
    def __init__(self):
        self.metadata_pipeline = MetadataGenerationPipeline()
        self.hierarchy_builder = ContextHierarchy()
        
    async def enrich_and_register(self, file_path: str):
        # 1. ファイル読み込み
        content = await self.read_file(file_path)
        
        # 2. メタデータ自動生成
        metadata = await self.metadata_pipeline.generate_metadata(
            file_path, 
            content
        )
        
        # 3. ヘッダー情報付与
        enriched_content = self._add_metadata_header(content, metadata)
        
        # 4. Cognee登録（メタデータ付き）
        result = await mcp__cognee__cognify(
            data=enriched_content,
            metadata=metadata.dict()  # メタデータを追加情報として渡す
        )
        
        # 5. インデックス更新
        await self._update_all_indexes(metadata)
        
        return result
        
    def _add_metadata_header(self, content: str, metadata: StandardizedMetadata) -> str:
        """ファイルヘッダーにメタデータを埋め込み"""
        header = f"""---
id: {metadata.id}
name: {metadata.name}
category: {metadata.category_l1}/{metadata.category_l2}/{metadata.category_l3}
tags: {', '.join(metadata.tags)}
keywords: {', '.join(metadata.keywords[:10])}
priority: {metadata.priority}
created: {metadata.created_at.isoformat()}
---

# 検索用メタデータ
Search Keywords: {', '.join(metadata.keywords)}
Related Topics: {', '.join(metadata.tags)}
Prerequisites: {', '.join(metadata.prerequisites)}

---

{content}
"""
        return header
```

### 4.3 パフォーマンス監視とフィードバック

```python
class SearchPerformanceMonitor:
    """
    検索パフォーマンスの継続的監視と最適化
    """
    def __init__(self):
        self.metrics = {
            'query_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'slow_queries': []
        }
        
    async def monitor_search(self, query: str, search_type: str):
        start_time = time.time()
        
        try:
            # 検索実行
            result = await self.execute_search(query, search_type)
            
            # メトリクス記録
            elapsed = time.time() - start_time
            self.metrics['query_times'].append(elapsed)
            
            if elapsed > 10.0:  # 10秒以上は遅いクエリ
                self.metrics['slow_queries'].append({
                    'query': query,
                    'type': search_type,
                    'time': elapsed
                })
                
            # 自動最適化トリガー
            if len(self.metrics['slow_queries']) > 10:
                await self.trigger_optimization()
                
            return result
            
        except Exception as e:
            self.log_error(query, search_type, e)
            raise
```

## 5. 実装ロードマップ

### Phase 1: 基盤構築（1-2週間）
1. L1キャッシュ層実装
2. 基本的なメタデータスキーマ定義
3. プライマリインデックス構築
4. 簡易的な段階検索実装

### Phase 2: 高度化（3-4週間）
1. 3層キャッシュシステム完成
2. 転置インデックス・ブルームフィルタ実装
3. 自動メタデータ生成パイプライン
4. 検索タイプ別最適化

### Phase 3: 統合・最適化（2-3週間）
1. 全システム統合
2. パフォーマンス監視システム
3. 自動最適化機能
4. A/Bテストと調整

## 6. 期待効果

### 定量的効果
- **検索速度**: 30秒 → 6秒（80%短縮）
- **キャッシュヒット率**: 0% → 60%（L1+L2+L3合計）
- **情報アクセス効率**: 70%向上
- **システム負荷**: 50%削減

### 定性的効果
- **ユーザー体験**: 即座に必要な情報にアクセス可能
- **開発効率**: AIエージェントの意思決定速度2倍
- **知識活用**: 埋もれた情報の発見率向上
- **スケーラビリティ**: 1000ファイル以上でも高速動作

## 7. 技術的考慮事項

### セキュリティ
- キャッシュデータの暗号化
- アクセス制御の維持
- 機密情報の適切な処理

### 可用性
- キャッシュ障害時のフォールバック
- インデックス再構築の自動化
- 部分的障害の分離

### 保守性
- モジュール化された設計
- 包括的なログとメトリクス
- 自動テストカバレッジ90%以上

## まとめ

本統合戦略により、Cogneeの検索機能は飛躍的に向上します。検索最適化エンジニア、データベースアーキテクト、メタデータスペシャリストの3つの専門性を統合することで、高速かつ高精度な検索システムを実現します。段階的な実装アプローチにより、リスクを最小化しながら着実に性能向上を達成できます。