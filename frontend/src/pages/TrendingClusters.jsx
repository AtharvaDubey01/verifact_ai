import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, RefreshCw } from 'lucide-react';
import { clustersAPI } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

function TrendingClusters() {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  useEffect(() => {
    loadClusters();
  }, []);
  
  const loadClusters = async () => {
    try {
      setLoading(true);
      const response = await clustersAPI.getClusters(20);
      setClusters(response.data.clusters);
    } catch (error) {
      console.error('Failed to load clusters:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await clustersAPI.refreshClusters(24);
      await loadClusters();
      alert('Clusters refreshed successfully!');
    } catch (error) {
      console.error('Failed to refresh clusters:', error);
      alert('Failed to refresh clusters. Please try again.');
    } finally {
      setRefreshing(false);
    }
  };
  
  if (loading) {
    return <LoadingSpinner text="Loading trending topics..." />;
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trending Topics</h1>
          <p className="text-gray-600 mt-1">
            Clustered claims showing viral misinformation patterns
          </p>
        </div>
        
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-primary flex items-center gap-2"
        >
          <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh Clusters
        </button>
      </div>
      
      {/* Clusters Grid */}
      {clusters.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No trending clusters found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {clusters.map((cluster) => (
            <ClusterCard key={cluster.cluster_id} cluster={cluster} />
          ))}
        </div>
      )}
    </div>
  );
}

function ClusterCard({ cluster }) {
  const trendLevel = cluster.trend_score >= 75 ? 'high' : 
                     cluster.trend_score >= 50 ? 'medium' : 'low';
  
  const trendColors = {
    high: 'bg-danger-100 text-danger-800 border-danger-300',
    medium: 'bg-warning-100 text-warning-800 border-warning-300',
    low: 'bg-blue-100 text-blue-800 border-blue-300',
  };
  
  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            {cluster.label}
          </h3>
          
          <div className="flex items-center gap-3 text-sm text-gray-600 mb-3">
            <span className="font-medium">{cluster.claim_count} claims</span>
            <span>•</span>
            <span className="capitalize">{cluster.category}</span>
          </div>
        </div>
        
        <div className={`px-3 py-1 rounded-full border font-medium text-sm ${trendColors[trendLevel]}`}>
          <TrendingUp className="w-4 h-4 inline mr-1" />
          {Math.round(cluster.trend_score)}
        </div>
      </div>
      
      <div className="p-4 bg-gray-50 rounded-lg mb-4">
        <p className="text-sm font-medium text-gray-700 mb-1">Representative Claim:</p>
        <p className="text-gray-900">{cluster.representative_claim}</p>
      </div>
      
      <Link
        to={`/claims`}
        className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium text-sm"
      >
        View All Claims in Cluster →
      </Link>
    </div>
  );
}

export default TrendingClusters;
