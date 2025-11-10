import { ExternalLink, CheckCircle } from 'lucide-react';

function EvidenceCard({ source }) {
  const reliabilityPercentage = Math.round(source.reliability_score * 100);
  
  const getReliabilityColor = (score) => {
    if (score >= 0.8) return 'text-success-600';
    if (score >= 0.6) return 'text-blue-600';
    if (score >= 0.4) return 'text-warning-600';
    return 'text-danger-600';
  };
  
  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">
            {source.title}
          </h4>
          <p className="text-sm text-gray-600">
            {source.domain}
          </p>
        </div>
        
        {/* Reliability Score */}
        <div className="flex flex-col items-end">
          <div className={`flex items-center gap-1 font-semibold ${getReliabilityColor(source.reliability_score)}`}>
            <CheckCircle className="w-4 h-4" />
            <span>{reliabilityPercentage}%</span>
          </div>
          <span className="text-xs text-gray-500">Reliability</span>
        </div>
      </div>
      
      {/* Excerpt */}
      <p className="text-gray-700 text-sm leading-relaxed mb-4">
        {source.excerpt}
      </p>
      
      {/* Footer */}
      <div className="flex items-center justify-between">
        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md capitalize">
          {source.source_type}
        </span>
        
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          <span>View Source</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
}

export default EvidenceCard;
