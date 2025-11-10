import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  ExternalLink, 
  Calendar,
  Tag,
  AlertCircle,
  CheckCircle2,
  MessageSquare,
  Play
} from 'lucide-react';
import { claimsAPI, verificationAPI, feedbackAPI } from '../api/client';
import VerdictPill from '../components/VerdictPill';
import EvidenceCard from '../components/EvidenceCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { format } from 'date-fns';

function ClaimDetail() {
  const { claimId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  
  useEffect(() => {
    loadClaimDetail();
  }, [claimId]);
  
  const loadClaimDetail = async () => {
    try {
      setLoading(true);
      const response = await claimsAPI.getClaimById(claimId);
      setData(response.data);
    } catch (error) {
      console.error('Failed to load claim:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleVerify = async () => {
    try {
      setVerifying(true);
      await verificationAPI.verifyClaim(claimId);
      await loadClaimDetail();
    } catch (error) {
      console.error('Verification failed:', error);
      alert('Verification failed. Please try again.');
    } finally {
      setVerifying(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner text="Loading claim details..." />;
  }
  
  if (!data) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-500">Claim not found.</p>
      </div>
    );
  }
  
  const { claim, verdict, evidence, similar_claims } = data;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link to="/claims" className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-4">
          <ArrowLeft className="w-4 h-4" />
          Back to Claims
        </Link>
        
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {claim.claim_text}
            </h1>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                <span>{format(new Date(claim.created_at), 'MMM d, yyyy HH:mm')}</span>
              </div>
              
              <div className="flex items-center gap-1">
                <Tag className="w-4 h-4" />
                <span className="capitalize">{claim.claim_type}</span>
              </div>
              
              <div className="flex items-center gap-1">
                <ExternalLink className="w-4 h-4" />
                <a 
                  href={claim.source} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary-600 hover:underline"
                >
                  View Source
                </a>
              </div>
            </div>
          </div>
          
          {!verdict && (
            <button 
              onClick={handleVerify}
              disabled={verifying}
              className="btn-primary flex items-center gap-2"
            >
              <Play className="w-5 h-5" />
              {verifying ? 'Verifying...' : 'Verify Claim'}
            </button>
          )}
        </div>
      </div>
      
      {/* Verdict Section */}
      {verdict && (
        <div className="card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Verdict</h2>
              <VerdictPill verdict={verdict.verdict} size="lg" />
            </div>
            
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">Confidence</div>
              <div className="text-3xl font-bold text-gray-900">
                {Math.round(verdict.confidence * 100)}%
              </div>
            </div>
          </div>
          
          {/* Harm Score */}
          {verdict.harm_score > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="font-medium text-gray-700">Harm Potential</span>
                <span className={`font-bold ${
                  verdict.harm_score >= 70 ? 'text-danger-600' :
                  verdict.harm_score >= 40 ? 'text-warning-600' :
                  'text-success-600'
                }`}>
                  {verdict.harm_score}/100
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all ${
                    verdict.harm_score >= 70 ? 'bg-danger-500' :
                    verdict.harm_score >= 40 ? 'bg-warning-500' :
                    'bg-success-500'
                  }`}
                  style={{ width: `${verdict.harm_score}%` }}
                />
              </div>
            </div>
          )}
          
          {/* Expert Reasoning */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">Expert Analysis</h3>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {verdict.reasoning}
            </p>
          </div>
          
          {/* Explain Like 12 */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900 mb-1">Simple Explanation</h4>
                <p className="text-blue-800 text-sm leading-relaxed">
                  {verdict.explain_like_12}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Evidence Sources */}
      {evidence && evidence.sources && evidence.sources.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Evidence Sources ({evidence.sources.length})
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {evidence.sources.map((source, idx) => (
              <EvidenceCard key={idx} source={source} />
            ))}
          </div>
        </div>
      )}
      
      {/* Similar Claims */}
      {similar_claims && similar_claims.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Similar Claims
          </h2>
          
          <div className="space-y-3">
            {similar_claims.map((similar, idx) => (
              <Link
                key={idx}
                to={`/claims/${similar.claim_id}`}
                className="block p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <p className="text-gray-900 flex-1">{similar.claim_text}</p>
                  <span className="text-sm font-medium text-primary-600">
                    {Math.round(similar.similarity_score * 100)}% match
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
      
      {/* Feedback Section */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Community Feedback</h2>
          <button 
            onClick={() => setShowFeedbackForm(!showFeedbackForm)}
            className="btn-secondary flex items-center gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            Submit Feedback
          </button>
        </div>
        
        {showFeedbackForm && (
          <FeedbackForm claimId={claimId} onSuccess={() => setShowFeedbackForm(false)} />
        )}
      </div>
    </div>
  );
}

function FeedbackForm({ claimId, onSuccess }) {
  const [formData, setFormData] = useState({
    feedback_type: 'correction',
    content: '',
    user_email: '',
  });
  const [submitting, setSubmitting] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setSubmitting(true);
      await feedbackAPI.submitFeedback({
        claim_id: claimId,
        ...formData
      });
      
      alert('Feedback submitted successfully!');
      onSuccess();
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Feedback Type
        </label>
        <select
          value={formData.feedback_type}
          onChange={(e) => setFormData({ ...formData, feedback_type: e.target.value })}
          className="input-field"
        >
          <option value="correction">Correction</option>
          <option value="appeal">Appeal Verdict</option>
          <option value="additional_evidence">Additional Evidence</option>
          <option value="other">Other</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Feedback
        </label>
        <textarea
          value={formData.content}
          onChange={(e) => setFormData({ ...formData, content: e.target.value })}
          className="input-field h-24"
          placeholder="Explain your feedback..."
          required
        />
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Email (optional)
        </label>
        <input
          type="email"
          value={formData.user_email}
          onChange={(e) => setFormData({ ...formData, user_email: e.target.value })}
          className="input-field"
          placeholder="your@email.com"
        />
      </div>
      
      <button 
        type="submit"
        disabled={submitting}
        className="btn-primary w-full"
      >
        {submitting ? 'Submitting...' : 'Submit Feedback'}
      </button>
    </form>
  );
}

export default ClaimDetail;
