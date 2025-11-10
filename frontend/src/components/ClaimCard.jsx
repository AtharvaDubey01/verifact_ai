import { Link } from 'react-router-dom';
import { Calendar, ExternalLink, Tag } from 'lucide-react';
import { format } from 'date-fns';
import VerdictPill from './VerdictPill';

function ClaimCard({ claim }) {
  return (
    <Link 
      to={`/claims/${claim.id}`}
      className="card hover:shadow-md transition-shadow duration-200 cursor-pointer"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          {/* Claim Text */}
          <p className="text-lg font-medium text-gray-900 mb-3 line-clamp-2">
            {claim.claim_text}
          </p>
          
          {/* Metadata */}
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              <span>{format(new Date(claim.created_at), 'MMM d, yyyy')}</span>
            </div>
            
            <div className="flex items-center gap-1">
              <Tag className="w-4 h-4" />
              <span className="capitalize">{claim.claim_type}</span>
            </div>
            
            <div className="flex items-center gap-1">
              <ExternalLink className="w-4 h-4" />
              <span className="capitalize">{claim.source_type}</span>
            </div>
          </div>
          
          {/* Entities */}
          {claim.entities && claim.entities.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {claim.entities.slice(0, 4).map((entity, idx) => (
                <span 
                  key={idx}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                >
                  {entity.text}
                </span>
              ))}
              {claim.entities.length > 4 && (
                <span className="px-2 py-1 text-gray-500 text-xs">
                  +{claim.entities.length - 4} more
                </span>
              )}
            </div>
          )}
          
          {/* Source */}
          <p className="text-xs text-gray-500 truncate">
            Source: {claim.source}
          </p>
        </div>
        
        {/* Verdict Pill */}
        <div className="flex-shrink-0">
          {claim.verdict_summary ? (
            <VerdictPill verdict={claim.verdict_summary} />
          ) : (
            <span className="px-3 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded-full">
              {claim.status}
            </span>
          )}
        </div>
      </div>
      
      {/* Confidence Bar */}
      {claim.confidence > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Detection Confidence</span>
            <span>{Math.round(claim.confidence * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all"
              style={{ width: `${claim.confidence * 100}%` }}
            />
          </div>
        </div>
      )}
    </Link>
  );
}

export default ClaimCard;
