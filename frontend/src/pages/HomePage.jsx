import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ImageUpload from '../components/ImageUpload';
import { uploadImage, startAnalysis } from '../services/api';
import { ArrowRightIcon } from '@heroicons/react/24/outline';

const HomePage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleImageSelected = (file) => {
    setSelectedImage(file);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      // Upload image
      const uploadedImage = await uploadImage(selectedImage);
      console.log('Image uploaded:', uploadedImage);

      // Start analysis
      const analysisJob = await startAnalysis(uploadedImage.id);
      console.log('Analysis started:', analysisJob);

      // Navigate to analysis page
      navigate(`/analysis/${uploadedImage.id}`, {
        state: { jobId: analysisJob.id }
      });
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to analyze image. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Analyze Your Items
        </h1>
        <p className="text-lg text-gray-600">
          Upload or capture an image to identify items and find marketplace values
        </p>
      </div>

      <div className="mb-8">
        <ImageUpload onImageSelected={handleImageSelected} />
      </div>

      {error && (
        <div className="max-w-2xl mx-auto mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {selectedImage && (
        <div className="max-w-2xl mx-auto">
          <button
            onClick={handleAnalyze}
            disabled={uploading}
            className="w-full flex items-center justify-center px-6 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading and Analyzing...
              </>
            ) : (
              <>
                Start Analysis
                <ArrowRightIcon className="ml-2 h-5 w-5" />
              </>
            )}
          </button>
        </div>
      )}

      <div className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">1</span>
            </div>
            <h3 className="font-semibold text-lg mb-2">Upload Image</h3>
            <p className="text-gray-600">Take a photo or upload an image of your item</p>
          </div>
          
          <div className="text-center">
            <div className="bg-blue-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">2</span>
            </div>
            <h3 className="font-semibold text-lg mb-2">AI Analysis</h3>
            <p className="text-gray-600">Our AI identifies objects and categories</p>
          </div>
          
          <div className="text-center">
            <div className="bg-blue-100 rounded-full h-16 w-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">3</span>
            </div>
            <h3 className="font-semibold text-lg mb-2">Find Values</h3>
            <p className="text-gray-600">Get prices from multiple marketplaces</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
