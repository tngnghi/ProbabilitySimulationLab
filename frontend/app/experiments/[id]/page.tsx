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

import { useParams } from 'next/navigation';

export default function ExperimentDetailPage() {
  const params = useParams();
  const experimentId = params.id;

  return (
    <div>
      <h1>Experiment {experimentId}</h1>
      <p>Details and data upload form go here.</p>
    </div>
  );
}