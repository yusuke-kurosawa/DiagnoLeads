import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ToastProvider } from './contexts/ToastContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { AssessmentsPage } from './pages/assessments/AssessmentsPage';
import { CreateAssessmentPage } from './pages/assessments/CreateAssessmentPage';
import { EditAssessmentPage } from './pages/assessments/EditAssessmentPage';
import { AssessmentDetailPage } from './pages/assessments/AssessmentDetailPage';
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
    <ToastProvider>
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

        {/* Assessment routes */}
        <Route
          path="/tenants/:tenantId/assessments"
          element={
            <ProtectedRoute>
              <AssessmentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/assessments/create"
          element={
            <ProtectedRoute>
              <CreateAssessmentPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/assessments/:assessmentId"
          element={
            <ProtectedRoute>
              <AssessmentDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tenants/:tenantId/assessments/:assessmentId/edit"
          element={
            <ProtectedRoute>
              <EditAssessmentPage />
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
    </ToastProvider>
  );
}

export default App;
