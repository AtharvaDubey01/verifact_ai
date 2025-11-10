import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  TrendingUp, 
  Users, 
  AlertTriangle,
  Shield
} from 'lucide-react';

function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/claims', label: 'Claims', icon: FileText },
    { path: '/trending', label: 'Trending Topics', icon: TrendingUp },
    { path: '/review', label: 'Human Review', icon: Users },
    { path: '/alerts', label: 'Alerts', icon: AlertTriangle },
  ];
  
  const isActive = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };
  
  return (
    <aside className="fixed left-0 top-16 h-screen w-64 bg-white border-r border-gray-200 z-10">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-lg">CrisisGuard AI</h2>
            <p className="text-xs text-gray-500">Fact Verification</p>
          </div>
        </div>
        
        <nav className="space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${active 
                    ? 'bg-primary-50 text-primary-700 font-medium' 
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}

export default Sidebar;
