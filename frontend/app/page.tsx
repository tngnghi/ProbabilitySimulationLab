'use client';   // needed if you use hooks (like redirect)

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { isLoggedIn } = useAuth();
  const router = useRouter();

  // If already logged in, send them straight to dashboard
  useEffect(() => {
    if (isLoggedIn) {
      router.push('/dashboard');
    }
  }, [isLoggedIn, router]);

  return (
    <main className="home-container">
      <h1>A/B Testing Platform with Statistical Inference</h1>
      <p className="home-subtitle">
        Design, run, and analyse A/B tests with confidence.
      </p>
      <div className="home-actions">
      </div>
    </main>
  );
}