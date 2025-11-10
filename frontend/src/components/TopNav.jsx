import { Bell, Search, User } from 'lucide-react';
import { useState } from 'react';

function TopNav() {
  const [searchQuery, setSearchQuery] = useState('');
  
  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-20">
      <div className="h-full px-6 flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search claims, topics, or sources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
        
        {/* Right Actions */}
        <div className="flex items-center gap-4 ml-6">
          {/* Notifications */}
          <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
            <Bell className="w-6 h-6" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-danger-500 rounded-full"></span>
          </button>
          
          {/* User Menu */}
          <button className="flex items-center gap-2 p-2 text-gray-700 hover:bg-gray-100 rounded-lg">
            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-primary-700" />
            </div>
            <span className="text-sm font-medium">Reviewer</span>
          </button>
        </div>
      </div>
    </nav>
  );
}

export default TopNav;
