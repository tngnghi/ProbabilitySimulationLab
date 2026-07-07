/*Purpose: Display analysis results and charts

Protected Route: Check authentication

Content (multi-section):

Section 1: Results Summary

Display:
  - Observed Lift (big number, highlight color)
  - P-Value (smaller number)
  - Significance (bold text: "SIGNIFICANT" or "NOT SIGNIFICANT")
  - Confidence Interval (ci_low to ci_high)
  - Summary text (plain English)

Section 2: Charts

if charts exist:
  For each chart in results.charts:
    Render using Plotly
    
    Component: <ChartDisplay chart={chart} />
    
    Plotly component:
      1. Create div with unique ID
      2. Call Plotly.newPlot(div, chart.data, chart.layout)
      3. On unmount: call Plotly.purge(div)

Section 3: Power Results (if computed)

Display:
  - Table: Effect Size | Power
  - Highlight effect size where power=80%
  - Explain: "You can detect a {effect}% lift with 80% power"

Section 4: Actions

Buttons:
  - Download Report (Week 10+)
  - Run Analysis Again (go back to experiment detail)
  - Back to Dashboard


Part 4: Reusable Components

Component 1: Navbar

Header with:
  - Logo (left)
  - Navigation links (center)
    - If not logged in: Login, Register
    - If logged in: Dashboard, Profile, Logout
  - User email (right, if logged in)

On Logout:
  - clearToken()
  - Redirect to /


Component 2: LoadingSpinner

Simple spinner to show while loading
  - Circle animation (CSS)
  - Text: "Loading..."
  
Usage:
  {isLoading && <LoadingSpinner />}


Component 3: ErrorAlert

Display error messages
  - Red background
  - Error message
  - Close button (dismiss)

Usage:
  {error && <ErrorAlert message={error} onClose={() => setError(null)} />}


Component 4: ChartDisplay

Render Plotly chart

Props:
  - data: Plotly trace data
  - layout: Plotly layout
  - title: chart title (optional)

Logic:
  1. useEffect:
     - Create div with unique ID
     - Call Plotly.newPlot(div, data, layout)
  2. On unmount:
     - Call Plotly.purge(div)
  3. On props change:
     - Update chart with Plotly.react()*/
'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ErrorAlert from '@/components/ErrorAlert';
import LoadingSpinner from '@/components/LoadingSpinner';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Helper to format numbers nicely
const fmt = (num: number, decimals = 4) => num.toFixed(decimals);
const fmtPercent = (num: number, decimals = 2) => (num * 100).toFixed(decimals) + '%';

export default function ResultsPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const runId = searchParams.get('run_id');
  const { token, isLoggedIn } = useAuth();
  const router = useRouter();

  const [run, setRun] = useState<any>(null);
  const [error, setError] = useState('');
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isLoggedIn) router.push('/login');
  }, [isLoggedIn, router]);

  useEffect(() => {
    if (!runId || !token) return;

    const poll = async () => {
      try {
        const res = await fetch(`${API_URL}/runs/${runId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error('Failed to fetch run status');
        const data = await res.json();
        setRun(data);

        if (data.status === 'success' || data.status === 'failed') {
          if (pollingRef.current) clearInterval(pollingRef.current);
        }
      } catch (err: any) {
        setError(err.message);
        if (pollingRef.current) clearInterval(pollingRef.current);
      }
    };

    poll();
    pollingRef.current = setInterval(poll, 2500);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [runId, token]);

  if (!isLoggedIn) return <LoadingSpinner />;
  if (!runId) return <ErrorAlert message="No run ID provided." />;

  return (
    <div className="results-page container">
      <h1>Analysis Results</h1>
      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      {!run ? (
        <LoadingSpinner text="Loading run status..." />
      ) : run.status === 'queued' || run.status === 'running' ? (
        <div className="run-progress">
          <LoadingSpinner text={`Analysis ${run.status}...`} />
          {run.progress !== undefined && <progress value={run.progress} max="1.0" />}
          <p>Please wait while we compute your results.</p>
        </div>
      ) : run.status === 'failed' ? (
        <div className="run-failed">
          <ErrorAlert message={`Analysis failed: ${run.error_message || 'Unknown error'}`} />
          <button onClick={() => router.push(`/experiments/${id}`)}>Back to Experiment</button>
        </div>
      ) : run.status === 'success' && run.results ? (
        <div className="results-card">
          {/* Summary highlight */}
          <div className={`result-banner ${run.results.significant ? 'significant' : 'not-significant'}`}>
            <h2>{run.results.significant ? 'Significant Result!' : 'Not Significant'}</h2>
            <p className="summary-text">{run.results.summary_json?.summary || run.results.summary}</p>
          </div>

          <div className="results-grid">
            <div className="result-item">
              <span className="label">Absolute Lift</span>
              <span className="value">{fmtPercent(run.results.absolute_lift, 2)}</span>
            </div>
            <div className="result-item">
              <span className="label">Relative Lift</span>
              <span className="value">{fmtPercent(run.results.relative_lift, 1)}</span>
            </div>
            <div className="result-item">
              <span className="label">P‑value</span>
              <span className="value">{fmt(run.results.p_value, 4)}</span>
            </div>
            <div className="result-item">
              <span className="label">Z‑Statistic</span>
              <span className="value">{fmt(run.results.z_statistic, 4)}</span>
            </div>
          </div>

          <div className="conversion-rates">
            <p>
              <strong>Control (A):</strong> {fmtPercent(run.results.conversion_rate_a, 2)} &nbsp;|&nbsp;
              <strong>Variant (B):</strong> {fmtPercent(run.results.conversion_rate_b, 2)}
            </p>
          </div>

          <div className="ci-box">
            <strong>95% Confidence Interval:</strong>
            <br />
            [{fmtPercent(run.results.absolute_lift_ci_low, 2)}, {fmtPercent(run.results.absolute_lift_ci_high, 2)}]
          </div>

          {run.results.charts && (
            <div className="charts">
              <p>Charts will render here.</p>
            </div>
          )}

          <button className="back-btn" onClick={() => router.push(`/experiments/${id}`)}>
            Back to Experiment
          </button>
        </div>
      ) : (
        <p>Unexpected run status.</p>
      )}
    </div>
  );
}