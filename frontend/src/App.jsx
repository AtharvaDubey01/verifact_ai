import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ClaimsList from './pages/ClaimsList';
import ClaimDetail from './pages/ClaimDetail';
import TrendingClusters from './pages/TrendingClusters';
import HumanReview from './pages/HumanReview';
import Alerts from './pages/Alerts';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="claims" element={<ClaimsList />} />
          <Route path="claims/:claimId" element={<ClaimDetail />} />
          <Route path="trending" element={<TrendingClusters />} />
          <Route path="review" element={<HumanReview />} />
          <Route path="alerts" element={<Alerts />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
