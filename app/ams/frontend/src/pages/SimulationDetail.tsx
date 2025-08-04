import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  Users,
  TrendingUp,
  BarChart3,
  Download,
  RefreshCw
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { api, createWebSocketConnection } from '../services/api';
import { SimulationResponse, SimulationStatus, SimulationResult, WebSocketMessage } from '../types/api';
import { format } from 'date-fns';

const SimulationDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const wsRef = useRef<WebSocket | null>(null);
  
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updates, setUpdates] = useState<string[]>([]);

  useEffect(() => {
    if (!id) return;

    const fetchSimulation = async () => {
      try {
        const data = await api.getSimulation(id);
        setSimulation(data);
        
        // If completed, fetch results
        if (data.status === SimulationStatus.COMPLETED) {
          const resultsData = await api.getSimulationResults(id);
          setResult(resultsData.result);
        }
        
        // Connect WebSocket if still running
        if (data.status === SimulationStatus.RUNNING || 
            data.status === SimulationStatus.INITIALIZING) {
          wsRef.current = createWebSocketConnection(id, handleWebSocketMessage);
        }
      } catch (err) {
        setError('Failed to fetch simulation details');
      } finally {
        setLoading(false);
      }
    };

    fetchSimulation();

    // Cleanup WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [id]);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    if (message.type === 'status_update') {
      setSimulation(prev => prev ? {
        ...prev,
        status: message.data.status || prev.status,
        progress: message.data.progress || prev.progress,
        updated_at: message.data.timestamp,
      } : null);
      
      // If completed, fetch results
      if (message.data.status === SimulationStatus.COMPLETED) {
        fetchResults();
      }
    }
    
    if (message.type === 'phase_update' && message.data.message) {
      setUpdates(prev => [...prev, `[${format(new Date(message.data.timestamp), 'HH:mm:ss')}] ${message.data.message}`]);
    }
  };

  const fetchResults = async () => {
    if (!id) return;
    try {
      const resultsData = await api.getSimulationResults(id);
      setResult(resultsData.result);
    } catch (err) {
      console.error('Failed to fetch results:', err);
    }
  };

  const getStatusIcon = (status: SimulationStatus) => {
    switch (status) {
      case SimulationStatus.COMPLETED:
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case SimulationStatus.FAILED:
        return <XCircle className="h-6 w-6 text-red-500" />;
      case SimulationStatus.RUNNING:
      case SimulationStatus.INITIALIZING:
        return <Clock className="h-6 w-6 text-blue-500 animate-pulse" />;
      default:
        return <AlertCircle className="h-6 w-6 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading simulation...</p>
        </div>
      </div>
    );
  }

  if (error || !simulation) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-700 dark:text-red-400">{error || 'Simulation not found'}</p>
      </div>
    );
  }

  // Prepare chart data
  const scoreData = result ? [
    { metric: 'Relevance', value: result.overall_relevance * 100 },
    { metric: 'Quality', value: result.overall_quality * 100 },
    { metric: 'Engagement', value: result.overall_engagement * 100 },
  ] : [];

  const radarData = result?.market_segments.map(segment => ({
    segment: segment.segment_name,
    relevance: (segment.average_scores.relevance || 0) * 100,
    quality: (segment.average_scores.quality || 0) * 100,
    engagement: (segment.average_scores.engagement || 0) * 100,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Simulation #{simulation.id}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Created {format(new Date(simulation.created_at), 'MMM d, yyyy HH:mm')}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {getStatusIcon(simulation.status)}
          <span className="text-lg font-medium text-gray-900 dark:text-white">
            {simulation.status}
          </span>
        </div>
      </div>

      {/* Progress Section */}
      {(simulation.status === SimulationStatus.RUNNING || 
        simulation.status === SimulationStatus.INITIALIZING) && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Simulation Progress
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600 dark:text-gray-400">Progress</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {Math.round(simulation.progress * 100)}%
                </span>
              </div>
              <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${simulation.progress * 100}%` }}
                />
              </div>
            </div>
            
            {/* Real-time Updates */}
            {updates.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Live Updates
                </h4>
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 max-h-40 overflow-y-auto">
                  {updates.slice(-5).map((update, idx) => (
                    <p key={idx} className="text-xs text-gray-600 dark:text-gray-400 font-mono">
                      {update}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error Section */}
      {simulation.status === SimulationStatus.FAILED && simulation.error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-700 dark:text-red-400 mb-2">
            Simulation Failed
          </h3>
          <p className="text-red-600 dark:text-red-400">{simulation.error}</p>
        </div>
      )}

      {/* Results Section */}
      {result && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Personas
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {result.total_personas}
                  </p>
                </div>
                <Users className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Avg Relevance
                  </p>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {(result.overall_relevance * 100).toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Avg Quality
                  </p>
                  <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {(result.overall_quality * 100).toFixed(1)}%
                  </p>
                </div>
                <BarChart3 className="h-8 w-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Processing Time
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {result.processing_time_seconds.toFixed(1)}s
                  </p>
                </div>
                <Clock className="h-8 w-8 text-gray-500" />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Overall Scores */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Overall Scores
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={scoreData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value) => `${value}%`} />
                  <Bar dataKey="value" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Market Segments Radar */}
            {radarData.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Market Segments Performance
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="segment" />
                    <PolarRadiusAxis domain={[0, 100]} />
                    <Radar name="Relevance" dataKey="relevance" stroke="#10B981" fill="#10B981" fillOpacity={0.6} />
                    <Radar name="Quality" dataKey="quality" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
                    <Radar name="Engagement" dataKey="engagement" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.6} />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Key Insights */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Key Insights
            </h3>
            <ul className="space-y-2">
              {result.key_insights.map((insight, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span className="text-gray-700 dark:text-gray-300">{insight}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommendations */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recommendations
            </h3>
            <ul className="space-y-2">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-green-500 mr-2">→</span>
                  <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default SimulationDetail;