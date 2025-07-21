# AMS-BD-004: リアルタイム可視化データ構造設計

## 1. 概要

本文書では、Article Market Simulatorのリアルタイム可視化を実現するためのデータ構造設計を定義します。サービスのコア価値となる美しくインタラクティブな可視化を支える技術基盤です。

## 2. 設計原則

### 2.1 効率性
- **差分更新**: 完全なスナップショットではなく、変更部分のみを送信
- **データ圧縮**: 冗長性を排除し、最小限のデータ転送
- **バッチング**: 複数の更新を効率的にまとめて送信

### 2.2 柔軟性
- **スキーマ進化**: 後方互換性を保ちながら拡張可能
- **選択的購読**: クライアントが必要なデータのみを購読
- **多様な可視化**: 同一データから複数の視覚表現を生成

### 2.3 リアルタイム性
- **低レイテンシ**: ミリ秒単位の更新反映
- **スケーラビリティ**: 多数のクライアント同時接続対応
- **品質調整**: ネットワーク状況に応じた適応的配信

## 3. コアデータモデル

### 3.1 基本構造
```typescript
// TypeScript定義（JSONスキーマの参考）
interface SimulationFrame {
  // メタデータ
  meta: {
    simulationId: string;
    timestamp: number;
    tick: number;
    frameType: 'snapshot' | 'delta';
  };
  
  // シミュレーション状態
  state: {
    agents: AgentState[];
    environment: EnvironmentState;
    metrics: MetricsSnapshot;
  };
  
  // 可視化ヒント
  visualization: {
    focusAreas: FocusArea[];
    animations: AnimationHint[];
    highlights: HighlightInstruction[];
  };
}
```

### 3.2 エージェント状態
```typescript
interface AgentState {
  id: string;
  type: string;
  
  // 位置情報（ネットワーク可視化用）
  position: {
    x: number;
    y: number;
    cluster?: string;
  };
  
  // 内部状態
  state: {
    phase: 'unaware' | 'exposed' | 'evaluating' | 'decided' | 'sharing';
    evaluation?: number;  // 0-1
    influence?: number;   // 0-1
  };
  
  // 関係性
  connections: {
    targetId: string;
    strength: number;
    type: 'social' | 'influence' | 'information';
  }[];
  
  // アニメーション用
  transitions: {
    property: string;
    from: any;
    to: any;
    duration: number;
  }[];
}
```

### 3.3 メトリクススナップショット
```typescript
interface MetricsSnapshot {
  // 集約値
  aggregate: {
    totalReach: number;
    activeAgents: number;
    sharingRate: number;
    sentimentScore: number;
  };
  
  // 時系列データポイント
  timeSeries: {
    [metricName: string]: {
      value: number;
      timestamp: number;
      trend: 'up' | 'down' | 'stable';
    }[];
  };
  
  // セグメント別分析
  segments: {
    [segmentId: string]: {
      count: number;
      metrics: { [key: string]: number };
    };
  };
}
```

## 4. ストリーミングプロトコル

### 4.1 WebSocketメッセージ形式
```typescript
// クライアント → サーバー
interface ClientMessage {
  type: 'subscribe' | 'unsubscribe' | 'configure';
  payload: {
    channels?: string[];
    resolution?: 'high' | 'medium' | 'low';
    dimensions?: VisualizationDimension[];
  };
}

// サーバー → クライアント
interface ServerMessage {
  type: 'frame' | 'event' | 'error';
  payload: SimulationFrame | EventData | ErrorInfo;
  sequence: number;  // メッセージ順序保証
}
```

### 4.2 差分エンコーディング
```typescript
interface DeltaFrame {
  meta: {
    baseFrameId: string;  // 基準となるスナップショット
    operations: DeltaOperation[];
  };
}

interface DeltaOperation {
  op: 'add' | 'update' | 'remove' | 'move';
  path: string;  // JSONPath形式
  value?: any;
  from?: string;  // moveオペレーション用
}
```

## 5. 可視化次元別データ構造

### 5.1 ネットワークグラフ
```typescript
interface NetworkGraphData {
  nodes: {
    id: string;
    label: string;
    size: number;
    color: string;
    metadata: any;
  }[];
  
  edges: {
    source: string;
    target: string;
    weight: number;
    type: string;
    animated?: boolean;
  }[];
  
  clusters?: {
    id: string;
    nodes: string[];
    label: string;
    color: string;
  }[];
}
```

### 5.2 時系列チャート
```typescript
interface TimeSeriesData {
  series: {
    name: string;
    data: [number, number][];  // [timestamp, value]
    type: 'line' | 'area' | 'bar';
    yAxis?: number;
  }[];
  
  annotations?: {
    timestamp: number;
    label: string;
    type: 'event' | 'phase';
  }[];
}
```

### 5.3 ヒートマップ
```typescript
interface HeatmapData {
  dimensions: {
    x: { labels: string[]; type: string; };
    y: { labels: string[]; type: string; };
  };
  
  cells: {
    x: number;
    y: number;
    value: number;
    label?: string;
  }[];
  
  colorScale: {
    min: number;
    max: number;
    scheme: string;
  };
}
```

## 6. 時系列データストレージ

### 6.1 データポイント構造
```json
{
  "measurement": "simulation_metrics",
  "tags": {
    "simulation_id": "sim_123",
    "metric_type": "reach",
    "segment": "early_adopters"
  },
  "fields": {
    "value": 42.5,
    "count": 15,
    "rate": 0.83
  },
  "timestamp": 1677649200000
}
```

### 6.2 集約クエリ対応
```sql
-- 5分間隔での集約例
SELECT 
  time_bucket('5 minutes', timestamp) as time,
  avg(value) as avg_value,
  max(value) as max_value,
  min(value) as min_value
FROM simulation_metrics
WHERE simulation_id = 'sim_123'
  AND timestamp > now() - interval '1 hour'
GROUP BY time
ORDER BY time DESC;
```

## 7. レポート生成用データ

### 7.1 Markdown用構造化データ
```typescript
interface ReportData {
  summary: {
    title: string;
    executionTime: string;
    keyFindings: string[];
  };
  
  sections: {
    title: string;
    content: string;
    charts?: ChartDefinition[];
    tables?: TableDefinition[];
  }[];
  
  appendix: {
    rawData?: any;
    methodology?: string;
    parameters?: any;
  };
}
```

### 7.2 チャート定義
```typescript
interface ChartDefinition {
  type: 'line' | 'bar' | 'pie' | 'network';
  title: string;
  data: any;  // チャートタイプ別のデータ
  options: {
    width?: number;
    height?: number;
    colors?: string[];
  };
  markdown: string;  // Markdown用のテキスト表現
}
```

## 8. パフォーマンス最適化

### 8.1 データサンプリング
```typescript
class AdaptiveSampler {
  sample(data: any[], targetSize: number): any[] {
    if (data.length <= targetSize) return data;
    
    // 重要度に基づくサンプリング
    const importance = data.map(d => this.calculateImportance(d));
    const threshold = this.findThreshold(importance, targetSize);
    
    return data.filter((d, i) => importance[i] >= threshold);
  }
  
  private calculateImportance(dataPoint: any): number {
    // 変化の大きさ、異常値、転換点などを考慮
    return dataPoint.changeRate * dataPoint.anomalyScore;
  }
}
```

### 8.2 圧縮戦略
```typescript
class DataCompressor {
  compress(frame: SimulationFrame): CompressedFrame {
    // 1. 数値の精度削減
    const quantized = this.quantizeNumbers(frame, 3);
    
    // 2. 繰り返しパターンの検出
    const patterns = this.detectPatterns(quantized);
    
    // 3. 差分エンコーディング
    const delta = this.createDelta(quantized, this.lastFrame);
    
    return {
      type: 'compressed',
      encoding: 'delta+pattern',
      data: delta,
      patterns: patterns
    };
  }
}
```

## 9. 実装例

### 9.1 ストリーミングサーバー
```python
class VisualizationStreamServer:
    def __init__(self):
        self.clients = {}
        self.compressor = DataCompressor()
        self.sampler = AdaptiveSampler()
    
    async def handle_client(self, websocket, path):
        client_id = str(uuid.uuid4())
        self.clients[client_id] = {
            'socket': websocket,
            'subscriptions': set(),
            'resolution': 'medium'
        }
        
        try:
            async for message in websocket:
                await self.process_message(client_id, message)
        finally:
            del self.clients[client_id]
    
    async def broadcast_frame(self, frame: SimulationFrame):
        # 各クライアントに最適化されたデータを送信
        for client_id, client in self.clients.items():
            optimized = self.optimize_for_client(frame, client)
            await client['socket'].send(json.dumps(optimized))
```

### 9.2 データ変換パイプライン
```python
class VisualizationPipeline:
    def transform_for_network_graph(self, state: SimulationState) -> NetworkGraphData:
        nodes = []
        edges = []
        
        for agent in state.agents:
            nodes.append({
                'id': agent.id,
                'label': agent.archetype,
                'size': agent.influence * 20 + 5,
                'color': self.phase_to_color(agent.phase)
            })
            
            for conn in agent.connections:
                if conn.strength > 0.1:  # 閾値以上のみ表示
                    edges.append({
                        'source': agent.id,
                        'target': conn.target_id,
                        'weight': conn.strength,
                        'type': conn.type
                    })
        
        return NetworkGraphData(nodes=nodes, edges=edges)
```

## 10. まとめ

このデータ構造設計により、以下を実現します：

1. **効率的なリアルタイム配信**: 差分更新とデータ圧縮による低レイテンシ
2. **柔軟な可視化対応**: 同一データから多様な視覚表現を生成
3. **スケーラブルなアーキテクチャ**: 多数のクライアント同時接続に対応
4. **将来の拡張性**: スキーマ進化による後方互換性の維持

これらの設計により、シミュレーションの「今」を美しく、そしてインタラクティブに表現することが可能となります。