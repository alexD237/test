import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Registre from "./pages/Registre";
import Depot from "./pages/Depot";
import Fiche from "./pages/Fiche";
import Reporting from "./pages/Reporting";
import AdminUtilisateurs from "./pages/AdminUtilisateurs";
import AdminAudit from "./pages/AdminAudit";
import AdminStats from "./pages/AdminStats";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Registre />} />
            <Route path="/depot" element={<Depot />} />
            <Route path="/courriers/:id" element={<Fiche />} />
            <Route path="/reporting" element={<Reporting />} />
            <Route
              path="/admin/utilisateurs"
              element={
                <AdminRoute>
                  <AdminUtilisateurs />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/audit"
              element={
                <AdminRoute>
                  <AdminAudit />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/stats"
              element={
                <AdminRoute>
                  <AdminStats />
                </AdminRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
