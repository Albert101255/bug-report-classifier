import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { Login } from './pages/Auth/Login';
import { Register } from './pages/Auth/Register';
import { Overview } from './pages/Overview/Overview';
import { IssueExplorer } from './pages/Issues/IssueExplorer';
import { CreateIssue } from './pages/Issues/CreateIssue';
import { IssueDetail } from './pages/Issues/IssueDetail';
import { TriageInbox } from './pages/Triage/TriageInbox';
import { Analytics } from './pages/Analytics/Analytics';
import { TeamsAndProjects } from './pages/Teams/TeamsAndProjects';
import { Settings } from './pages/Settings/Settings';
import { ModelManagement } from './pages/Models/ModelManagement';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-xs font-mono">
        Loading workspace session...
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

const RoleAwareIndex: React.FC = () => {
  const { user } = useAuth();
  if (user?.role === 'ORG_ADMIN') {
    return <Overview />;
  }
  return <Navigate to="/issues/new" replace />;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter basename={import.meta.env.BASE_URL || '/'}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<RoleAwareIndex />} />
              <Route path="issues" element={<IssueExplorer />} />
              <Route path="issues/new" element={<CreateIssue />} />
              <Route path="issues/:id" element={<IssueDetail />} />
              <Route path="triage" element={<TriageInbox />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="teams" element={<TeamsAndProjects />} />
              <Route path="settings" element={<Settings />} />
              <Route path="models" element={<ModelManagement />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
