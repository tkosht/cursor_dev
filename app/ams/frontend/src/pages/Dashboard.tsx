import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Plus, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  TrendingUp,
  Users,
  BarChart3
} from 'lucide-react';
import { api } from '../services/api';
import { SimulationResponse, SimulationStatus } from '../types/api';
import { format } from 'date-fns';

const Dashboard = () => {
  const [simulations, setSimulations] = useState<SimulationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Mock data for demo - replace with actual API calls
  useEffect(() => {
    const fetchSimulations = async () => {
      try {
        // For demo, create mock data
        const mockSimulations: SimulationResponse[] = [
          {
            id: '1',
            status: SimulationStatus.COMPLETED,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            progress: 1.0,
          },
          {
            id: '2',
            status: SimulationStatus.RUNNING,
            created_at: new Date(Date.now() - 3600000).toISOString(),
            updated_at: new Date().toISOString(),
            progress: 0.65,
          },
        ];
        setSimulations(mockSimulations);
      } catch (err) {
        setError('Failed to fetch simulations');
      } finally {
        setLoading(false);
      }
    };

    fetchSimulations();
  }, []);

  const getStatusIcon = (status: SimulationStatus) => {
    switch (status) {
      case SimulationStatus.COMPLETED:
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case SimulationStatus.FAILED:
        return <XCircle className="h-5 w-5 text-red-500" />;
      case SimulationStatus.RUNNING:
      case SimulationStatus.INITIALIZING:
        return <Clock className="h-5 w-5 text-blue-500 animate-pulse" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: SimulationStatus) => {
    switch (status) {
      case SimulationStatus.COMPLETED:
        return 'text-green-700 bg-green-50 dark:text-green-400 dark:bg-green-900/20';
      case SimulationStatus.FAILED:
        return 'text-red-700 bg-red-50 dark:text-red-400 dark:bg-red-900/20';
      case SimulationStatus.RUNNING:
      case SimulationStatus.INITIALIZING:
        return 'text-blue-700 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20';
      default:
        return 'text-gray-700 bg-gray-50 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading simulations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-700 dark:text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Simulation Dashboard
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor and manage your article evaluation simulations
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Simulations
              </p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {simulations.length}
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Completed
              </p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                {simulations.filter(s => s.status === SimulationStatus.COMPLETED).length}
              </p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Running
              </p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {simulations.filter(s => 
                  s.status === SimulationStatus.RUNNING || 
                  s.status === SimulationStatus.INITIALIZING
                ).length}
              </p>
            </div>
            <Clock className="h-8 w-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Action Button */}
      <div className="mb-6">
        <Link
          to="/simulations/new"
          className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          New Simulation
        </Link>
      </div>

      {/* Simulations List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Recent Simulations
          </h3>
        </div>
        
        {simulations.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No simulations yet
            </p>
            <Link
              to="/simulations/new"
              className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create Your First Simulation
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {simulations.map((simulation) => (
              <Link
                key={simulation.id}
                to={`/simulations/${simulation.id}`}
                className="block px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(simulation.status)}
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        Simulation #{simulation.id}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Created {format(new Date(simulation.created_at), 'MMM d, yyyy HH:mm')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {/* Progress Bar */}
                    {(simulation.status === SimulationStatus.RUNNING || 
                      simulation.status === SimulationStatus.INITIALIZING) && (
                      <div className="w-32">
                        <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${simulation.progress * 100}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {Math.round(simulation.progress * 100)}%
                        </p>
                      </div>
                    )}
                    
                    {/* Status Badge */}
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(simulation.status)}`}>
                      {simulation.status}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;