import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { ToastProvider } from './contexts/ToastContext';
import { Layout } from './components/layout/Layout';
import { ErrorBoundary } from './components/ErrorBoundary';
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
import ComponentsShowcase from './pages/ComponentsShowcase';
import AdminMasterPage from './pages/admin/AdminMasterPage';
import AuditLogPage from './pages/admin/AuditLogPage';
import SettingsPage from './pages/settings/SettingsPage';
import ErrorPage from './pages/ErrorPage';
import './App.css';

// Protected Route wrapper with Layout
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
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
      <ErrorBoundary>
        <Router>
          <Routes>
          {/* Error Routes */}
          <Route path="/error" element={<ErrorPage />} />

          {/* 404 Fallback */}
          <Route path="*" element={<ErrorPage />} />
        {/* Public routes - no layout */}
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

        {/* Protected routes - all wrapped with Layout */}
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

        {/* Admin Master Management routes */}
        <Route
          path="/tenants/:tenantId/admin/masters"
          element={
            <ProtectedRoute>
              <AdminMasterPage />
            </ProtectedRoute>
          }
        />

        {/* Admin Audit Log routes */}
        <Route
          path="/tenants/:tenantId/admin/audit-logs"
          element={
            <ProtectedRoute>
              <AuditLogPage />
            </ProtectedRoute>
          }
        />

        {/* Settings routes */}
        <Route
          path="/tenants/:tenantId/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />

        {/* Components Showcase (Demo) */}
        <Route path="/components" element={<ComponentsShowcase />} />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </ErrorBoundary>
    </ToastProvider>
  );
}

export default App;
