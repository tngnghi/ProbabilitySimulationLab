/*Purpose: List user's experiments, create new one

Protected Route: Redirect to /login if not authenticated

Content (two sections):

Section 1: Experiment List

if experiments.length === 0:
  Show "No experiments yet. Create one to get started."

else:
  Show table/cards:
    Columns: Name, Created, Status, Data Uploaded?, Actions
    
    Name: clickable link to /experiments/{id}
    Created: formatted date (e.g., "Jan 28, 2025")
    Status: "Ready for analysis" or "Waiting for data"
    Data: "✓" or "-"
    Actions: View button, Delete button

Section 2: Create Experiment Form

Form fields:
  - Name (text input, required)
  - Description (textarea, optional)
  - Alpha (dropdown: 0.05, 0.01, 0.10, default 0.05)
  - Two-sided (checkbox, default true)
  - Metric (dropdown: conversion, click-through-rate, etc.)

On Submit:
  1. Call apiCall('POST /experiments', {...})
  2. If success:
     - Add to experiments list (update UI)
     - Clear form
     - Show "Experiment created" message
  3. If error:
     - Show error message

On Load:

1. Check if logged in (getToken() returns token)
2. If not: redirect to /login
3. If yes: fetch experiments
4. Call apiCall('GET /experiments', {})
5. Display list*/
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { isLoggedIn } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoggedIn) router.push('/login');
  }, [isLoggedIn, router]);

  if (!isLoggedIn) return <p>Redirecting...</p>;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>You have 0 experiments.</p>
    </div>
  );
}