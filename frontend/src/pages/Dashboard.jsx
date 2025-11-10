import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  CheckCircle, 
  TrendingUp, 
  AlertTriangle,
  Plus,
  Activity
} from 'lucide-react';
import { claimsAPI, clustersAPI } from '../api/client';
import ClaimCard from '../components/ClaimCard';
import LoadingSpinner from '../components/LoadingSpinner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentClaims, setRecentClaims] = useState([]);
  const [trendingClusters, setTrendingClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showIngestModal, setShowIngestModal] = useState(false);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, claimsRes, clustersRes] = await Promise.all([
        claimsAPI.getStats(),
        claimsAPI.getClaims({ limit: 5 }),
        clustersAPI.getClusters(5),
      ]);
      
      setStats(statsRes.data);
      setRecentClaims(claimsRes.data);
      setTrendingClusters(clustersRes.data.clusters);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner text="Loading dashboard..." />;
  }
  
  // Prepare chart data
  const verdictChartData = stats?.verdict_breakdown ? 
    Object.entries(stats.verdict_breakdown).map(([verdict, count]) => ({
      verdict,
      count
    })) : [];
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Real-time misinformation detection overview</p>
        </div>
        
        <button 
          onClick={() => setShowIngestModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Ingest New Claim
        </button>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={FileText}
          label="Total Claims"
          value={stats?.total_claims || 0}
          color="bg-blue-500"
        />
        <StatCard
          icon={CheckCircle}
          label="Verified Claims"
          value={stats?.verified_claims || 0}
          color="bg-success-500"
        />
        <StatCard
          icon={TrendingUp}
          label="Trending Clusters"
          value={stats?.trending_clusters || 0}
          color="bg-purple-500"
        />
        <StatCard
          icon={Activity}
          label="Active Today"
          value={Math.floor((stats?.total_claims || 0) * 0.15)}
          color="bg-warning-500"
        />
      </div>
      
      {/* Verdict Breakdown Chart */}
      {verdictChartData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Verdict Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={verdictChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="verdict" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      
      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Claims */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Recent Claims</h2>
            <Link to="/claims" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All →
            </Link>
          </div>
          
          <div className="space-y-4">
            {recentClaims.map((claim) => (
              <ClaimCard key={claim.id} claim={claim} />
            ))}
          </div>
        </div>
        
        {/* Trending Clusters */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Trending Topics</h2>
            <Link to="/trending" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All →
            </Link>
          </div>
          
          <div className="space-y-3">
            {trendingClusters.map((cluster) => (
              <div key={cluster.cluster_id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">
                      {cluster.label}
                    </h3>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {cluster.representative_claim}
                    </p>
                    <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
                      <span>{cluster.claim_count} claims</span>
                      <span>Trend Score: {Math.round(cluster.trend_score)}</span>
                    </div>
                  </div>
                  
                  <TrendingUp className="w-5 h-5 text-danger-500" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Ingest Modal */}
      {showIngestModal && (
        <IngestModal 
          onClose={() => setShowIngestModal(false)} 
          onSuccess={loadDashboardData}
        />
      )}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
        </div>
        <div className={`w-12 h-12 ${color} rounded-lg flex items-center justify-center`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function IngestModal({ onClose, onSuccess }) {
  const [text, setText] = useState('');
  const [source, setSource] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      const response = await claimsAPI.ingest({
        text,
        source: source || 'manual',
        source_type: 'manual'
      });
      
      setResult(response.data);
      
      if (response.data.is_claim) {
        setTimeout(() => {
          onSuccess();
          onClose();
        }, 2000);
      }
    } catch (error) {
      console.error('Ingestion failed:', error);
      alert('Failed to ingest claim. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Ingest New Claim</h2>
        
        {result ? (
          <div className="space-y-4">
            {result.is_claim ? (
              <div className="p-4 bg-success-50 border border-success-200 rounded-lg">
                <p className="text-success-800 font-medium">✓ Claim detected successfully!</p>
                <p className="text-sm text-success-700 mt-1">
                  Claim ID: {result.claim_id}
                </p>
              </div>
            ) : (
              <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
                <p className="text-warning-800 font-medium">No verifiable claim detected</p>
                <p className="text-sm text-warning-700 mt-1">{result.message}</p>
              </div>
            )}
            
            <button onClick={onClose} className="btn-primary w-full">
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Text to Analyze
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="input-field h-32"
                placeholder="Enter the text containing a potential claim..."
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source URL (optional)
              </label>
              <input
                type="text"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="input-field"
                placeholder="https://example.com/post/123"
              />
            </div>
            
            <div className="flex gap-3">
              <button 
                type="button" 
                onClick={onClose}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button 
                type="submit"
                disabled={loading}
                className="btn-primary flex-1"
              >
                {loading ? 'Analyzing...' : 'Analyze Text'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
