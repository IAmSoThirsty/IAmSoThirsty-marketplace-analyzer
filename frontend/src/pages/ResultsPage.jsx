import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalysis, startMarketplaceSearch, getMarketplaceJob, getMarketplaceItems } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import ProgressBar from '../components/ProgressBar';
import MarketplaceCard from '../components/MarketplaceCard';

const ResultsPage = () => {
  const { analysisId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [job, setJob] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [selectedProviders, setSelectedProviders] = useState(['ebay', 'amazon', 'stockx', 'grailed']);

  const { message } = useWebSocket(job?.id);

  useEffect(() => {
    loadAnalysis();
    loadMarketplaceItems();
  }, [analysisId]);

  useEffect(() => {
    if (message && message.type === 'job_update' && message.job_id === job?.id) {
      setJob(prevJob => ({
        ...prevJob,
        status: message.status,
        progress: message.progress,
        result: message.result,
      }));

      if (message.status === 'completed') {
        loadMarketplaceItems();
      }
    }
  }, [message]);

  const loadAnalysis = async () => {
    try {
      const analysisData = await getAnalysis(analysisId);
      setAnalysis(analysisData);
    } catch (err) {
      console.error('Error loading analysis:', err);
      setError('Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const loadMarketplaceItems = async () => {
    try {
      const itemsData = await getMarketplaceItems(analysisId);
      setItems(itemsData);
    } catch (err) {
      console.error('Error loading marketplace items:', err);
    }
  };

  const handleSearch = async () => {
    setSearching(true);
    setError(null);

    try {
      const searchJob = await startMarketplaceSearch(analysisId, selectedProviders);
      setJob(searchJob);
    } catch (err) {
      console.error('Error starting search:', err);
      setError('Failed to start marketplace search');
    } finally {
      setSearching(false);
    }
  };

  const toggleProvider = (provider) => {
    setSelectedProviders(prev => 
      prev.includes(provider)
        ? prev.filter(p => p !== provider)
        : [...prev, provider]
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Marketplace Results</h1>

      {analysis && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Detected Items</h2>
          <div className="flex flex-wrap gap-2">
            {analysis.labels.map((label, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {label}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Search Marketplaces</h2>
        
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Select marketplaces to search:</p>
          <div className="flex flex-wrap gap-2">
            {['ebay', 'amazon', 'stockx', 'grailed'].map(provider => (
              <button
                key={provider}
                onClick={() => toggleProvider(provider)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedProviders.includes(provider)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {job && (
          <div className="mb-4">
            <ProgressBar
              progress={job.progress || 0}
              status={job.status}
              message="Searching marketplaces..."
            />
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        <button
          onClick={handleSearch}
          disabled={searching || selectedProviders.length === 0}
          className="w-full px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {searching ? 'Searching...' : 'Search Selected Marketplaces'}
        </button>
      </div>

      {items.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Found {items.length} Items
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {items.map((item, index) => (
              <MarketplaceCard key={index} item={item} />
            ))}
          </div>
        </div>
      )}

      {items.length === 0 && !job && (
        <div className="text-center py-12">
          <p className="text-gray-600">
            No marketplace items found yet. Click "Search Selected Marketplaces" to find prices.
          </p>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
