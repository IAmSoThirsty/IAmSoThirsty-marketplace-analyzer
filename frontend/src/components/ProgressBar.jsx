import { useEffect } from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

const ProgressBar = ({ progress, status, message }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-600';
      case 'failed':
        return 'bg-red-600';
      case 'processing':
        return 'bg-blue-600';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'processing':
        return 'Processing...';
      case 'pending':
        return 'Pending...';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">
          {message || getStatusText()}
        </span>
        <span className="text-sm font-medium text-gray-700">
          {progress}%
        </span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {status === 'completed' && (
        <div className="flex items-center mt-2 text-green-600">
          <CheckCircleIcon className="h-5 w-5 mr-1" />
          <span className="text-sm font-medium">Complete!</span>
        </div>
      )}

      {status === 'failed' && (
        <div className="mt-2 text-red-600">
          <span className="text-sm font-medium">An error occurred</span>
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
