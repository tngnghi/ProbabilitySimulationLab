'use client';

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FiLogOut, FiUser } from 'react-icons/fi'; // optional icons

export default function Navbar() {
  const { isLoggedIn, user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout(); // clears token, resets state, redirects to '/'
  };

  return (
    <header className="navbar">
      {/* Left – Logo */}
      <div className="navbar__left">
        <Link href="/" className="logo">
          <span className="logo-text">SimStat</span>
        </Link>
      </div>

      {/* Center – Navigation Links */}
      <nav className="navbar__center">
        {isLoggedIn ? (
          <>
            <Link href="/dashboard" className="nav-link">Dashboard</Link>
            <Link href="/profile" className="nav-link">Profile</Link>
          </>
        ) : (
          <>
            <Link href="/login" className="nav-link">Login</Link>
            <Link href="/register" className="nav-link">Register</Link>
          </>
        )}
      </nav>

      {/* Right – Email + Logout (only if logged in) */}
      <div className="navbar__right">
        {isLoggedIn && user && (
          <div className="user-area">
            <span className="user-email">
              <FiUser className="icon" /> {user.email}
            </span>
            <button onClick={handleLogout} className="logout-btn" aria-label="Logout">
              <FiLogOut className="icon" />
              <span className="logout-text">Logout</span>
            </button>
          </div>
        )}
      </div>
    </header>
  );
}