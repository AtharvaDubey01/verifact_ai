import { useState, useEffect } from 'react';
import { Filter } from 'lucide-react';
import { claimsAPI } from '../api/client';
import ClaimCard from '../components/ClaimCard';
import LoadingSpinner from '../components/LoadingSpinner';

function ClaimsList() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    claim_type: '',
    status: '',
    search: '',
  });
  
  useEffect(() => {
    loadClaims();
  }, [filters]);
  
  const loadClaims = async () => {
    try {
      setLoading(true);
      const params = {};
      
      if (filters.claim_type) params.claim_type = filters.claim_type;
      if (filters.status) params.status = filters.status;
      if (filters.search) params.search = filters.search;
      
      const response = await claimsAPI.getClaims(params);
      setClaims(response.data);
    } catch (error) {
      console.error('Failed to load claims:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">All Claims</h1>
        <p className="text-gray-600 mt-1">Browse and search all detected claims</p>
      </div>
      
      {/* Filters */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Claim Type
            </label>
            <select
              value={filters.claim_type}
              onChange={(e) => setFilters({ ...filters, claim_type: e.target.value })}
              className="input-field"
            >
              <option value="">All Types</option>
              <option value="health">Health</option>
              <option value="politics">Politics</option>
              <option value="science">Science</option>
              <option value="business">Business</option>
              <option value="general">General</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="input-field"
            >
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="processing">Processing</option>
              <option value="verified">Verified</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="input-field"
              placeholder="Search claims..."
            />
          </div>
        </div>
      </div>
      
      {/* Claims List */}
      {loading ? (
        <LoadingSpinner text="Loading claims..." />
      ) : claims.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No claims found matching your filters.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {claims.map((claim) => (
            <ClaimCard key={claim.id} claim={claim} />
          ))}
        </div>
      )}
    </div>
  );
}

export default ClaimsList;
