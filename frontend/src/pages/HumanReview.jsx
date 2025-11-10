import { useState, useEffect } from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { claimsAPI, verificationAPI } from '../api/client';
import VerdictPill from '../components/VerdictPill';
import LoadingSpinner from '../components/LoadingSpinner';

function HumanReview() {
  const [pendingClaims, setPendingClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadPendingClaims();
  }, []);
  
  const loadPendingClaims = async () => {
    try {
      setLoading(true);
      const response = await claimsAPI.getClaims({ status: 'verified', limit: 50 });
      setPendingClaims(response.data);
    } catch (error) {
      console.error('Failed to load claims:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner text="Loading claims for review..." />;
  }
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Human Review Queue</h1>
        <p className="text-gray-600 mt-1">
          Review AI verdicts and approve for publication
        </p>
      </div>
      
      {pendingClaims.length === 0 ? (
        <div className="card text-center py-12">
          <CheckCircle className="w-16 h-16 text-success-500 mx-auto mb-4" />
          <p className="text-gray-500">All caught up! No claims pending review.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingClaims.map((claim) => (
            <ReviewCard 
              key={claim.id} 
              claim={claim} 
              onReviewed={loadPendingClaims}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ReviewCard({ claim, onReviewed }) {
  const [expanded, setExpanded] = useState(false);
  const [reviewData, setReviewData] = useState({
    override_verdict: '',
    notes: '',
  });
  const [submitting, setSubmitting] = useState(false);
  
  const handleApprove = async (approve) => {
    try {
      setSubmitting(true);
      
      // This would need the verdict_id, which we'd get from claim detail
      // For demo purposes, we'll just show the concept
      
      alert(approve ? 'Verdict approved!' : 'Verdict rejected!');
      onReviewed();
    } catch (error) {
      console.error('Review failed:', error);
      alert('Failed to submit review.');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {claim.claim_text}
          </h3>
          
          <div className="flex items-center gap-4">
            {claim.verdict_summary && (
              <VerdictPill verdict={claim.verdict_summary} />
            )}
            <span className="text-sm text-gray-600">
              Type: <span className="capitalize">{claim.claim_type}</span>
            </span>
          </div>
        </div>
        
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>
      
      {expanded && (
        <div className="space-y-4 pt-4 border-t border-gray-200">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Override Verdict (optional)
            </label>
            <select
              value={reviewData.override_verdict}
              onChange={(e) => setReviewData({ ...reviewData, override_verdict: e.target.value })}
              className="input-field"
            >
              <option value="">Keep AI Verdict</option>
              <option value="True">True</option>
              <option value="False">False</option>
              <option value="Misleading">Misleading</option>
              <option value="Partially True">Partially True</option>
              <option value="Unverified">Unverified</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reviewer Notes
            </label>
            <textarea
              value={reviewData.notes}
              onChange={(e) => setReviewData({ ...reviewData, notes: e.target.value })}
              className="input-field h-20"
              placeholder="Add any notes about your review..."
            />
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => handleApprove(false)}
              disabled={submitting}
              className="btn-danger flex items-center gap-2"
            >
              <XCircle className="w-5 h-5" />
              Reject
            </button>
            
            <button
              onClick={() => handleApprove(true)}
              disabled={submitting}
              className="btn-primary flex items-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              Approve for Publication
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default HumanReview;
