import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Toaster } from "sonner";
import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Onboarding from "./pages/Onboarding";
import Waiting from "./pages/Waiting";
import Dashboard from "./pages/Dashboard";
import Kundali from "./pages/Kundali";
import Inbox from "./pages/Inbox";
import Invitations from "./pages/Invitations";
import Profile from "./pages/Profile";
import Admin from "./pages/Admin";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import PaymentSuccess from "./pages/PaymentSuccess";
import PaymentCancel from "./pages/PaymentCancel";

function Protected({ children, needsProfile = true }) {
  const { user, loading } = useAuth();
  if (loading || user === null) {
    return <div className="min-h-screen flex items-center justify-center text-[#8A6B72]">Aligning stars...</div>;
  }
  if (!user) return <Navigate to="/login" replace />;
  if (needsProfile && !user.profile_complete) return <Navigate to="/onboarding" replace />;
  return children;
}

function LoggedInRedirect({ children }) {
  const { user, loading } = useAuth();
  if (loading || user === null) return <div className="min-h-screen flex items-center justify-center text-[#8A6B72]">...</div>;
  if (user) return <Navigate to={user.profile_complete ? "/dashboard" : "/onboarding"} replace />;
  return children;
}

function Shell() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<LoggedInRedirect><Login /></LoggedInRedirect>} />
        <Route path="/forgot-password" element={<LoggedInRedirect><ForgotPassword /></LoggedInRedirect>} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
        <Route path="/register" element={<LoggedInRedirect><Register /></LoggedInRedirect>} />
        <Route path="/invite/:code" element={<LoggedInRedirect><Register /></LoggedInRedirect>} />
        <Route path="/onboarding" element={<Protected needsProfile={false}><Onboarding /></Protected>} />
        <Route path="/waiting" element={<Protected><Waiting /></Protected>} />
        <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
        <Route path="/kundali/:matchId" element={<Protected><Kundali /></Protected>} />
        <Route path="/inbox" element={<Protected><Inbox /></Protected>} />
        <Route path="/invitations" element={<Protected><Invitations /></Protected>} />
        <Route path="/profile" element={<Protected><Profile /></Protected>} />
        <Route path="/admin" element={<Protected needsProfile={false}><Admin /></Protected>} />
        <Route path="/payment/success" element={<Protected><PaymentSuccess /></Protected>} />
        <Route path="/payment/cancel" element={<Protected><PaymentCancel /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster theme="dark" position="top-right" />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Shell />
      </AuthProvider>
    </BrowserRouter>
  );
}
