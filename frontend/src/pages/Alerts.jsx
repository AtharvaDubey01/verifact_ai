import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Bell } from 'lucide-react';
import { alertsAPI } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import { format } from 'date-fns';

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  
  useEffect(() => {
    loadAlerts();
  }, [filter]);
  
  const loadAlerts = async () => {
    try {
      setLoading(true);
      const params = { is_active: filter !== 'resolved' };
      if (filter !== 'all' && filter !== 'resolved') {
        params.severity = filter;
      }
      
      const response = await alertsAPI.getAlerts(params);
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleResolve = async (alertId) => {
    try {
      await alertsAPI.resolveAlert(alertId);
      await loadAlerts();
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      alert('Failed to resolve alert.');
    }
  };
  
  if (loading) {
    return <LoadingSpinner text="Loading alerts..." />;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h1>
          <p className="text-gray-600 mt-1">
            Monitor high-harm claims and system alerts
          </p>
        </div>
        
        <button className="btn-primary flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Subscribe to Alerts
        </button>
      </div>
      
      {/* Filter Tabs */}
      <div className="flex gap-2">
        {['all', 'critical', 'high', 'medium', 'resolved'].map((filterOption) => (
          <button
            key={filterOption}
            onClick={() => setFilter(filterOption)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors capitalize ${
              filter === filterOption
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {filterOption}
          </button>
        ))}
      </div>
      
      {/* Alerts List */}
      {alerts.length === 0 ? (
        <div className="card text-center py-12">
          <CheckCircle className="w-16 h-16 text-success-500 mx-auto mb-4" />
          <p className="text-gray-500">No alerts matching your filter.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <AlertCard 
              key={alert.id} 
              alert={alert}
              onResolve={() => handleResolve(alert.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AlertCard({ alert, onResolve }) {
  const severityConfig = {
    critical: {
      color: 'border-danger-500 bg-danger-50',
      badge: 'bg-danger-600 text-white',
      icon: 'text-danger-600'
    },
    high: {
      color: 'border-warning-500 bg-warning-50',
      badge: 'bg-warning-600 text-white',
      icon: 'text-warning-600'
    },
    medium: {
      color: 'border-blue-500 bg-blue-50',
      badge: 'bg-blue-600 text-white',
      icon: 'text-blue-600'
    },
    low: {
      color: 'border-gray-300 bg-gray-50',
      badge: 'bg-gray-600 text-white',
      icon: 'text-gray-600'
    }
  };
  
  const config = severityConfig[alert.severity] || severityConfig.low;
  
  return (
    <div className={`p-6 border-l-4 rounded-lg ${config.color}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4 flex-1">
          <AlertTriangle className={`w-6 h-6 ${config.icon} flex-shrink-0 mt-1`} />
          
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-lg font-bold text-gray-900">
                {alert.title}
              </h3>
              <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${config.badge}`}>
                {alert.severity}
              </span>
            </div>
            
            <p className="text-gray-700 mb-3">
              {alert.description}
            </p>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>Type: {alert.alert_type.replace('_', ' ')}</span>
              <span>•</span>
              <span>{format(new Date(alert.created_at), 'MMM d, yyyy HH:mm')}</span>
              {alert.related_claim_ids && alert.related_claim_ids.length > 0 && (
                <>
                  <span>•</span>
                  <span>{alert.related_claim_ids.length} related claims</span>
                </>
              )}
            </div>
          </div>
        </div>
        
        {alert.is_active && (
          <button
            onClick={onResolve}
            className="btn-secondary ml-4"
          >
            Resolve
          </button>
        )}
      </div>
    </div>
  );
}

export default Alerts;
