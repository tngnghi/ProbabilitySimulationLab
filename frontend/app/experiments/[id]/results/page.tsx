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