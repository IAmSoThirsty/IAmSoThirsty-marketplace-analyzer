const MarketplaceCard = ({ item }) => {
  const formatPrice = (price, currency) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(price || 0);
  };

  const getProviderColor = (provider) => {
    const colors = {
      ebay: 'bg-yellow-100 text-yellow-800',
      amazon: 'bg-orange-100 text-orange-800',
      stockx: 'bg-green-100 text-green-800',
      grailed: 'bg-purple-100 text-purple-800',
    };
    return colors[provider] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4">
      <div className="flex items-start space-x-4">
        {item.image_url && (
          <img
            src={item.image_url}
            alt={item.item_name}
            className="w-24 h-24 object-cover rounded"
          />
        )}
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${getProviderColor(item.provider)}`}>
              {item.provider.toUpperCase()}
            </span>
            {item.relevance_score && (
              <span className="text-xs text-gray-500">
                Match: {(item.relevance_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
          
          <h3 className="text-sm font-semibold text-gray-900 truncate mb-1">
            {item.item_name}
          </h3>
          
          <div className="flex items-center justify-between">
            <p className="text-lg font-bold text-blue-600">
              {formatPrice(item.price, item.currency)}
            </p>
            {item.condition && (
              <span className="text-xs text-gray-600">{item.condition}</span>
            )}
          </div>
          
          {item.availability && (
            <p className="text-xs text-gray-500 mt-1">{item.availability}</p>
          )}
          
          {item.item_url && (
            <a
              href={item.item_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-2 text-sm text-blue-600 hover:text-blue-800"
            >
              View Item →
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketplaceCard;
