/*Purpose: View experiment, upload data, run analysis

Protected Route: Redirect to /login if not authenticated

Layout (three sections):

Section 1: Experiment Info (read-only)

Display:
  - Name
  - Description
  - Alpha
  - Two-sided
  - Created date
  - Edit button (optional)

Section 2: Data Upload

if data already uploaded:
  Display:
    - n_a, conv_a
    - n_b, conv_b
    - Conversion rates (computed)
    - Lift (computed)
    - Warnings (if any)
  Button: "Re-upload Data"

else:
  Show upload form:
    - n_a (number input)
    - conv_a (number input)
    - n_b (number input)
    - conv_b (number input)
    
  On Submit:
    1. Validate (conv_a <= n_a, etc.)
    2. Call apiCall('POST /experiments/{id}/data/aggregate', {...})
    3. If success:
       - Display uploaded data
       - Show "Data uploaded" message
       - Display any warnings
    4. If error (422):
       - Show validation error

Section 3: Run Analysis

if no data uploaded:
  Show message: "Upload data first"
  Disable Run button

else:
  Show run form:
    - Method (radio buttons: Z-Test, Permutation)
    - If Permutation:
        - n_sim (number input, default 20000)
        - seed (number input, default 42)
    - Compute Power (checkbox, default false)
    - If compute power:
        - Baseline rate (number input)
        - Effect grid (text area, comma-separated)
    
  Button: "Run Analysis"
    
  On Submit:
    1. Validate inputs
    2. Call apiCall('POST /experiments/{id}/runs', {...})
    3. Get run_id from response
    4. Redirect to /experiments/{id}/results?run_id={run_id}*/
  
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ErrorAlert from '@/components/ErrorAlert';
import LoadingSpinner from '@/components/LoadingSpinner';
import { apiCall } from '@/lib/api';

export default function ExperimentDetailPage() {
  const { id } = useParams();
  const { isLoggedIn } = useAuth();
  const router = useRouter();

  const [experiment, setExperiment] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Data upload
  const [nA, setNA] = useState('');
  const [convA, setConvA] = useState('');
  const [nB, setNB] = useState('');
  const [convB, setConvB] = useState('');
  const [uploading, setUploading] = useState(false);

  // Run analysis
  const [method, setMethod] = useState('ztest');
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!isLoggedIn) { router.push('/login'); return; }
    fetchExperiment();
  }, [id, isLoggedIn]);

  const fetchExperiment = async () => {
    try {
      const data = await apiCall(`/experiments/${id}`);
      setExperiment(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const n_a = parseInt(nA), conv_a = parseInt(convA), n_b = parseInt(nB), conv_b = parseInt(convB);
    if (conv_a > n_a || conv_b > n_b) {
      setError('Conversions cannot exceed total count');
      return;
    }
    setUploading(true);
    try {
      const result = await apiCall(`/experiments/${id}/data/aggregate`, {
        method: 'POST',
        body: JSON.stringify({ n_a, conv_a, n_b, conv_b }),
      });
      setExperiment({ ...experiment, data: result });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    setError('');
    setRunning(true);
    try {
      const runData = await apiCall<any>(`/experiments/${id}/runs`, {
        method: 'POST',
        body: JSON.stringify({ method }),
      });
      router.push(`/experiments/${id}/results?run_id=${runData.id}`);

      console.log('Run response:', runData);

      const runId = runData.id;

      if (!runId) {
        setError('Analysis started but no run ID returned.');
        return;
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  };

  if (!isLoggedIn || loading) return <LoadingSpinner />;
  if (error && !experiment) return <ErrorAlert message={error} />;

  const data = experiment?.data;

  return (
    <div className="experiment-detail">
      {error && <ErrorAlert message={error} onClose={() => setError('')} />}
      <h1>{experiment.name}</h1>
      <p>{experiment.description}</p>
      <p>Alpha: {experiment.alpha} | Two-sided: {experiment.two_sided ? 'Yes' : 'No'} | Metric: {experiment.metric}</p>

      <section className="data-section">
        <h2>Data</h2>
        {data ? (
          <div>
            <p>Group A: {data.conv_a} / {data.n_a} ({(data.conv_rate_a * 100).toFixed(1)}%)</p>
            <p>Group B: {data.conv_b} / {data.n_b} ({(data.conv_rate_b * 100).toFixed(1)}%)</p>
            <p>Observed Lift: {data.observed_lift}</p>
          </div>
        ) : (
          <p>No data uploaded yet.</p>
        )}

        <form onSubmit={handleUpload}>
          <label>n_a</label><input type="number" required value={nA} onChange={e => setNA(e.target.value)} />
          <label>conv_a</label><input type="number" required value={convA} onChange={e => setConvA(e.target.value)} />
          <label>n_b</label><input type="number" required value={nB} onChange={e => setNB(e.target.value)} />
          <label>conv_b</label><input type="number" required value={convB} onChange={e => setConvB(e.target.value)} />
          <button type="submit" disabled={uploading}>
            {uploading ? 'Uploading...' : (data ? 'Re-upload Data' : 'Upload Data')}
          </button>
        </form>
      </section>

      <section className="analysis-section">
        <h2>Run Analysis</h2>
        {!data ? (
          <p>Upload data first.</p>
        ) : (
          <div>
            <label>Method:</label>
            <select value={method} onChange={e => setMethod(e.target.value)}>
              <option value="ztest">Z-Test</option>
              <option value="permutation">Permutation</option>
            </select>
            <button onClick={handleRunAnalysis} disabled={running}>
              {running ? 'Starting...' : 'Run Analysis'}
            </button>
          </div>
        )}
      </section>
    </div>
  );
}