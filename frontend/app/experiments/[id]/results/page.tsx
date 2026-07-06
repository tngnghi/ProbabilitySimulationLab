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

import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ErrorAlert from '@/components/ErrorAlert';
import LoadingSpinner from '@/components/LoadingSpinner';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export default function ResultsPage() {
  const { id } = useParams();
  const searchParams = useSearchParams();
  const runId = searchParams.get('run_id');
  const { token, isLoggedIn } = useAuth();
  const router = useRouter();
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoggedIn) { router.push('/login'); return; }
    if (!runId) { setError('No run ID provided'); setLoading(false); return; }
    fetchResults();
  }, [runId, isLoggedIn]);

  const fetchResults = async () => {
    try {
      const res = await fetch(`${API_URL}/runs/${runId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to load results');
      const data = await res.json();
      // If run is still processing, you might need to poll, but for simplicity assume immediate
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isLoggedIn || loading) return <LoadingSpinner />;
  if (error) return <ErrorAlert message={error} />;
  if (!results) return <p>No results found.</p>;

  return (
    <div className="results-page">
      <h1>Results for Experiment {id}</h1>
      <div className="summary">
        <p>Observed Lift: {results.results?.observed_lift ?? 'N/A'}</p>
        <p>P-value: {results.results?.p_value ?? 'N/A'}</p>
        <p>Significant: {results.results?.significant ? 'Yes' : 'No'}</p>
        <p>Confidence Interval: [{results.results?.ci_low}, {results.results?.ci_high}]</p>
        <p>{results.results?.summary}</p>
      </div>
      {results.results?.charts && (
        <div className="charts">
          {/* You can integrate Plotly here later */}
          <p>Charts will render here.</p>
        </div>
      )}
      <button onClick={() => router.push(`/experiments/${id}`)}>Back to Experiment</button>
    </div>
  );
}