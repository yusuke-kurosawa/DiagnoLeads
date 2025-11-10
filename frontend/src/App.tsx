import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { LeadsPage } from './pages/leads/LeadsPage';
import { CreateLeadPage } from './pages/leads/CreateLeadPage';
import { EditLeadPage } from './pages/leads/EditLeadPage';
import { LeadDetailPage } from './pages/leads/LeadDetailPage';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import './App.css';

// Protected Route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Public Route wrapper (redirect to dashboard if already authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Lead routes */}
        <Route
          path="/tenants/:tenantId/leads"
          element={
            <ProtectedRoute>
              <LeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/leads/create"
          element={
            <ProtectedRoute>
              <CreateLeadPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/leads/:leadId"
          element={
            <ProtectedRoute>
              <LeadDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/leads/:leadId/edit"
          element={
            <ProtectedRoute>
              <EditLeadPage />
            </ProtectedRoute>
          }
        />

        {/* Analytics routes */}
        <Route
          path="/tenants/:tenantId/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
