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
import { apiCall } from '@/lib/api';
import ErrorAlert from '@/components/ErrorAlert';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function DashboardPage() {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  const [experiments, setExperiments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
  }, [isLoggedIn, router]);

  const fetchExperiments = async () => {
    try {
      const data = await apiCall<any[]>('/experiments');
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
      await apiCall('/experiments', {
        method: 'POST',
        body: JSON.stringify({
          name,
          description,
          alpha,
          two_sided: twoSided,
          metric,
        }),
      });
      await fetchExperiments();
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
    <div className="dashboard container">
      <h1>Dashboard</h1>
      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      {/* Experiment list */}
      <section className="experiments-section">
        <h2>Your Experiments</h2>
        {experiments.length === 0 ? (
          <div className="empty-state">
            <p>No experiments yet. Create your first one!</p>
          </div>
        ) : (
          <div className="experiment-grid">
            {experiments.map((exp: any) => (
              <Link href={`/experiments/${exp.id}`} key={exp.id} className="experiment-card">
                <div className="card-header">
                  <h3>{exp.name}</h3>
                  <span className="card-date">
                    {new Date(exp.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="card-description">
                  {exp.description || 'No description'}
                </p>
                <div className="card-meta">
                  <span>α: {exp.alpha}</span>
                  <span>{exp.two_sided ? 'Two‑sided' : 'One‑sided'}</span>
                  <span>{exp.metric}</span>
                </div>
                <div className="card-arrow">→</div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Create form */}
      <section className="create-section">
        <h2>Create New Experiment</h2>
        <form onSubmit={handleCreate} className="create-form">
          <div className="form-row">
            <label>
              Name *
              <input
                type="text"
                required
                placeholder="e.g., Homepage Button Test"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label>
              Metric
              <select value={metric} onChange={(e) => setMetric(e.target.value)}>
                <option value="conversion">Conversion</option>
                <option value="click-through-rate">Click‑through Rate</option>
              </select>
            </label>
          </div>

          <label>
            Description
            <textarea
              rows={2}
              placeholder="Optional description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </label>

          <div className="form-row">
            <label>
              Alpha
              <select value={alpha} onChange={(e) => setAlpha(parseFloat(e.target.value))}>
                <option value={0.01}>0.01</option>
                <option value={0.05}>0.05</option>
                <option value={0.10}>0.10</option>
              </select>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={twoSided}
                onChange={(e) => setTwoSided(e.target.checked)}
              />
              Two‑sided test
            </label>
          </div>

          <button type="submit" disabled={creating} className="btn btn-primary">
            {creating ? 'Creating...' : 'Create Experiment'}
          </button>
        </form>
      </section>
    </div>
  );
}