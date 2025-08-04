import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Send, Settings, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { SimulationConfig } from '../types/api';

const SimulationCreate = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [articleContent, setArticleContent] = useState('');
  const [articleTitle, setArticleTitle] = useState('');
  const [articleAuthor, setArticleAuthor] = useState('');
  const [articleCategory, setArticleCategory] = useState('');
  
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [config, setConfig] = useState<SimulationConfig>({
    num_personas: 50,
    diversity_level: 0.7,
    analysis_depth: 'standard',
    llm_provider: 'gemini',
    parallel_processing: true,
    include_minority_perspectives: true,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!articleContent.trim()) {
      setError('Article content is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.createSimulation({
        article_content: articleContent,
        article_metadata: {
          title: articleTitle || undefined,
          author: articleAuthor || undefined,
          category: articleCategory || undefined,
          published_date: new Date().toISOString(),
        },
        config,
      });

      // Navigate to simulation detail page
      navigate(`/simulations/${response.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create simulation');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Create New Simulation
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Analyze how different personas will react to your article
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-700 dark:text-red-400">{error}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Article Content Section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <FileText className="h-5 w-5 text-gray-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Article Information
            </h3>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title (Optional)
              </label>
              <input
                type="text"
                id="title"
                value={articleTitle}
                onChange={(e) => setArticleTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Enter article title"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="author" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Author (Optional)
                </label>
                <input
                  type="text"
                  id="author"
                  value={articleAuthor}
                  onChange={(e) => setArticleAuthor(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Author name"
                />
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Category (Optional)
                </label>
                <input
                  type="text"
                  id="category"
                  value={articleCategory}
                  onChange={(e) => setArticleCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="e.g., Technology, Science"
                />
              </div>
            </div>

            <div>
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Article Content <span className="text-red-500">*</span>
              </label>
              <textarea
                id="content"
                value={articleContent}
                onChange={(e) => setArticleContent(e.target.value)}
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Paste or type your article content here..."
                required
              />
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                The full text of the article you want to analyze
              </p>
            </div>
          </div>
        </div>

        {/* Advanced Configuration */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center justify-between w-full mb-4"
          >
            <div className="flex items-center">
              <Settings className="h-5 w-5 text-gray-500 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Advanced Configuration
              </h3>
            </div>
            <span className="text-sm text-gray-500">
              {showAdvanced ? '−' : '+'}
            </span>
          </button>

          {showAdvanced && (
            <div className="space-y-4">
              <div>
                <label htmlFor="num_personas" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Number of Personas ({config.num_personas})
                </label>
                <input
                  type="range"
                  id="num_personas"
                  min="10"
                  max="200"
                  step="10"
                  value={config.num_personas}
                  onChange={(e) => setConfig({ ...config, num_personas: parseInt(e.target.value) })}
                  className="w-full"
                />
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  More personas provide broader perspective but take longer
                </p>
              </div>

              <div>
                <label htmlFor="diversity_level" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Diversity Level ({(config.diversity_level! * 100).toFixed(0)}%)
                </label>
                <input
                  type="range"
                  id="diversity_level"
                  min="0"
                  max="100"
                  step="10"
                  value={(config.diversity_level || 0.7) * 100}
                  onChange={(e) => setConfig({ ...config, diversity_level: parseInt(e.target.value) / 100 })}
                  className="w-full"
                />
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Higher diversity creates more varied persona perspectives
                </p>
              </div>

              <div>
                <label htmlFor="analysis_depth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Analysis Depth
                </label>
                <select
                  id="analysis_depth"
                  value={config.analysis_depth}
                  onChange={(e) => setConfig({ ...config, analysis_depth: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="quick">Quick (5-10 minutes)</option>
                  <option value="standard">Standard (10-20 minutes)</option>
                  <option value="deep">Deep (20-40 minutes)</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.parallel_processing}
                    onChange={(e) => setConfig({ ...config, parallel_processing: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Enable parallel processing (faster but uses more resources)
                  </span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={config.include_minority_perspectives}
                    onChange={(e) => setConfig({ ...config, include_minority_perspectives: e.target.checked })}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Include minority perspectives
                  </span>
                </label>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || !articleContent.trim()}
            className="inline-flex items-center px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Start Simulation
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SimulationCreate;