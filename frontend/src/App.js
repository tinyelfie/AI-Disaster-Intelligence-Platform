import React, { useState } from "react";
import "./index.css";
import "./App.css";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import SignIn from "./pages/SignIn";
import Dashboard from "./pages/Dashboard";
import DisasterCenter from "./pages/DisasterCenter";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Legal from "./pages/Legal";
import BackendPending from "./pages/BackendPending";

// ── Hardcoded credentials (portfolio demo) ────────────────────────────────────
const VALID_USERS = {
  admin:    { password: "disaster123", name: "Admin Analyst",    email: "admin@terra-aura.dev" },
  analyst:  { password: "terra2024",   name: "Dr. Aris Thorne",  email: "analyst@terra-aura.dev" },
};

// ── Pages that need the sidebar / topbar shell ────────────────────────────────
const SHELL_PAGES = [
  "dashboard", "disaster-center", "analytics", "reports",
  "profile", "legal", "support", "system-status", "backend-pending",
];

function renderPage(page, user, navigate, logout) {
  switch (page) {
    case "dashboard":       return <Dashboard       user={user} onNavigate={navigate} />;
    case "disaster-center": return <DisasterCenter  user={user} onNavigate={navigate} />;
    case "analytics":       return <Analytics               onNavigate={navigate} />;
    case "reports":         return <Reports                 onNavigate={navigate} />;
    case "profile":         return <Profile         user={user} onNavigate={navigate} onLogout={logout} />;
    case "legal":           return <Legal                   onNavigate={navigate} />;
    case "support":         return <BackendPending          onNavigate={navigate} />;
    case "system-status":   return <BackendPending          onNavigate={navigate} />;
    case "backend-pending": return <BackendPending          onNavigate={navigate} />;
    default:                return <BackendPending          onNavigate={navigate} />;
  }
}

export default function App() {
  const [user, setUser]           = useState(null);
  const [activePage, setActivePage] = useState("dashboard");

  // ── Auth ──────────────────────────────────────────────────────────────────
  const signIn = (username, password) => {
    const match = VALID_USERS[username?.toLowerCase()];
    if (match && match.password === password) {
      setUser({ name: match.name, email: match.email, username });
      setActivePage("dashboard");
      return null;   // no error
    }
    // SSO / social sign-in paths (any username passed with no password check)
    if (password === "__sso__") {
      setUser({ name: username, email: `${username}@terra-aura.dev`, username });
      setActivePage("dashboard");
      return null;
    }
    return "Invalid credentials. Try admin / disaster123";
  };

  const logout = () => {
    setUser(null);
    setActivePage("dashboard");
  };

  const navigate = (page) => {
    if (page === "logout") { logout(); return; }
    setActivePage(page);
  };

  // ── Gate: show sign-in when not authenticated ─────────────────────────────
  if (!user) {
    return <SignIn onSignIn={signIn} />;
  }

  // ── Authenticated shell ───────────────────────────────────────────────────
  return (
    <div className="app-shell">
      <Sidebar active={activePage} onNavigate={navigate} />

      <div className="app-main">
        {/* DisasterCenter has its own topbar built-in */}
        {activePage !== "disaster-center" && (
          <Topbar user={user} activePage={activePage} onNavigate={navigate} />
        )}

        <div className="app-content">
          {renderPage(activePage, user, navigate, logout)}
        </div>
      </div>
    </div>
  );
}
