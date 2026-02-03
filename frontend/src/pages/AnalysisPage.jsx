import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getImage, getAnalysisJob, getImageAnalyses, getImageDownloadUrl } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import ProgressBar from '../components/ProgressBar';
import ResultCard from '../components/ResultCard';

const AnalysisPage = () => {
  const { imageId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [image, setImage] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [job, setJob] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const jobId = location.state?.jobId || null;
  const { message, isConnected } = useWebSocket(jobId);

  useEffect(() => {
    loadImageData();
  }, [imageId]);

  useEffect(() => {
    if (jobId) {
      loadJobStatus();
    }
  }, [jobId]);

  useEffect(() => {
    if (message) {
      console.log('WebSocket message:', message);
      if (message.type === 'job_update' && message.job_id === jobId) {
        setJob(prevJob => ({
          ...prevJob,
          status: message.status,
          progress: message.progress,
          result: message.result,
        }));

        if (message.status === 'completed') {
          loadAnalyses();
        }
      }
    }
  }, [message]);

  const loadImageData = async () => {
    try {
      const imageData = await getImage(imageId);
      setImage(imageData);

      const urlData = await getImageDownloadUrl(imageId);
      setImageUrl(urlData.url);

      await loadAnalyses();
    } catch (err) {
      console.error('Error loading image:', err);
      setError('Failed to load image data');
    } finally {
      setLoading(false);
    }
  };

  const loadJobStatus = async () => {
    try {
      const jobData = await getAnalysisJob(jobId);
      setJob(jobData);
    } catch (err) {
      console.error('Error loading job:', err);
    }
  };

  const loadAnalyses = async () => {
    try {
      const analysesData = await getImageAnalyses(imageId);
      setAnalyses(analysesData);
    } catch (err) {
      console.error('Error loading analyses:', err);
    }
  };

  const handleFindPrices = (analysisId) => {
    navigate(`/results/${analysisId}`);
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

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  const latestAnalysis = analyses.length > 0 ? analyses[0] : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Image Analysis</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Your Image</h2>
          {imageUrl && (
            <img 
              src={imageUrl} 
              alt="Uploaded" 
              className="w-full rounded-lg shadow-lg"
            />
          )}
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Analysis Status</h2>
          
          {job && (
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <ProgressBar 
                progress={job.progress || 0}
                status={job.status}
                message={`Analyzing image... ${job.progress || 0}%`}
              />
              
              {job.status === 'failed' && job.error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-800">{job.error}</p>
                </div>
              )}
            </div>
          )}

          {latestAnalysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Detection Results</h3>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  Model: {latestAnalysis.model_type} 
                  {latestAnalysis.model_version && ` (${latestAnalysis.model_version})`}
                </p>
                {latestAnalysis.processing_time && (
                  <p className="text-sm text-gray-600">
                    Processing time: {latestAnalysis.processing_time.toFixed(2)}s
                  </p>
                )}
              </div>

              <div className="space-y-3">
                {latestAnalysis.detections && latestAnalysis.detections.slice(0, 5).map((detection, index) => (
                  <ResultCard
                    key={index}
                    label={detection.label}
                    confidence={detection.confidence}
                    bbox={detection.bbox}
                  />
                ))}
              </div>

              <button
                onClick={() => handleFindPrices(latestAnalysis.id)}
                className="w-full mt-6 px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
              >
                Find Marketplace Prices
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
