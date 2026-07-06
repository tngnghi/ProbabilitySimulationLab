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

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ErrorAlert from '@/components/ErrorAlert';
import LoadingSpinner from '@/components/LoadingSpinner';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function DashboardPage() {
  const { token, isLoggedIn } = useAuth();
  const router = useRouter();
  const [experiments, setExperiments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [alpha, setAlpha] = useState(0.05);
  const [twoSided, setTwoSided] = useState(true);
  const [metric, setMetric] = useState('conversion');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!isLoggedIn) {
      router.push('/login');
      return;
    }
    fetchExperiments();
  }, [isLoggedIn]);

  const fetchExperiments = async () => {
    try {
      const res = await fetch(`${API_URL}/experiments`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load experiments');
      const data = await res.json();
      setExperiments(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/experiments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description, alpha, two_sided: twoSided, metric }),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to create experiment');
      }
      // Refresh list
      await fetchExperiments();
      // Clear form
      setName('');
      setDescription('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  if (!isLoggedIn) return <LoadingSpinner />;
  if (loading) return <LoadingSpinner />;

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      <section className="experiment-list">
        <h2>Your Experiments</h2>
        {experiments.length === 0 ? (
          <p>No experiments yet. Create one below.</p>
        ) : (
          <ul>
            {experiments.map((exp: any) => (
              <li key={exp.id}>
                <Link href={`/experiments/${exp.id}`}>{exp.name}</Link>
                <span>Created: {new Date(exp.created_at).toLocaleDateString()}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="create-experiment">
        <h2>Create New Experiment</h2>
        <form onSubmit={handleCreate}>
          <label>Name (required)</label>
          <input type="text" required value={name} onChange={e => setName(e.target.value)} />
          <label>Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} />
          <label>Alpha</label>
          <select value={alpha} onChange={e => setAlpha(parseFloat(e.target.value))}>
            <option value={0.01}>0.01</option>
            <option value={0.05}>0.05</option>
            <option value={0.10}>0.10</option>
          </select>
          <label>
            <input type="checkbox" checked={twoSided} onChange={e => setTwoSided(e.target.checked)} />
            Two-sided test
          </label>
          <label>Metric</label>
          <select value={metric} onChange={e => setMetric(e.target.value)}>
            <option value="conversion">Conversion</option>
            <option value="click-through-rate">Click-through Rate</option>
          </select>
          <button type="submit" disabled={creating}>
            {creating ? 'Creating...' : 'Create Experiment'}
          </button>
        </form>
      </section>
    </div>
  );
}