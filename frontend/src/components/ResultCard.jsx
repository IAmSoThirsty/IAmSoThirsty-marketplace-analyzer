const ResultCard = ({ label, confidence, bbox }) => {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{label}</h3>
          <p className="text-sm text-gray-600 mt-1">
            Confidence: {(confidence * 100).toFixed(1)}%
          </p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          confidence > 0.8 ? 'bg-green-100 text-green-800' :
          confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {confidence > 0.8 ? 'High' :
           confidence > 0.6 ? 'Medium' :
           'Low'}
        </div>
      </div>
      
      {bbox && (
        <div className="mt-2 text-xs text-gray-500">
          Bounding box: [{bbox.map(v => v.toFixed(0)).join(', ')}]
        </div>
      )}
    </div>
  );
};

export default ResultCard;
