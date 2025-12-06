# Add Streamlit Web UI for Weather Data Visualization

## Why
Currently, users can only view weather data through command-line interface (CLI) tools, which requires technical knowledge and is not user-friendly for non-technical users. A web-based interface would make the weather data more accessible and easier to explore interactively.

This addresses the need for:
- User-friendly visualization of temperature forecasts
- Interactive location selection without command-line knowledge
- Visual charts and graphs for better data understanding
- Easy access from any device with a web browser

## What Changes
- Add Streamlit web framework for creating interactive web UI
- Create `streamlit_app.py` with temperature visualization
- Implement location dropdown selector for filtering data
- Add temperature charts showing max/min trends
- Display data table with filtering options
- Add summary statistics for selected location
- Update dependencies (add streamlit, pandas, plotly)

**Breaking Changes:**
- None - This is purely additive functionality

## Impact

### Affected Specs
- **NEW**: `specs/data-visualization/spec.md` - Web UI visualization requirements

### Affected Code
- **NEW**: `streamlit_app.py` - Main Streamlit application
- **NEW**: `requirements.txt` - Python dependencies
- `README.md` - Add Streamlit usage instructions

### External Dependencies
- `streamlit` - Web framework for data apps
- `pandas` - Data manipulation (likely already available)
- `plotly` - Interactive charts (optional, can use streamlit native charts)

### User Impact
- Users can now access weather data through web browser at `http://localhost:8501`
- Location selection via dropdown instead of command-line arguments
- Visual charts for temperature trends
- No impact on existing CLI tools (crawler.py, query_db.py)

## Risks
- **Risk**: Streamlit adds significant dependency size
  - **Mitigation**: Document as optional feature, keep CLI tools functional
  
- **Risk**: Port 8501 may be occupied
  - **Mitigation**: Document how to change port with --server.port flag

- **Risk**: Users unfamiliar with Streamlit may have setup issues
  - **Mitigation**: Provide clear installation and usage instructions

## Timeline
- Estimated effort: 2-3 hours
- Immediate implementation for course demo
