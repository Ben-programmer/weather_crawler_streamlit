# Project Context

## Purpose
This project is a weather data crawler system that fetches agricultural weather forecast data from Taiwan's Central Weather Administration (CWA) Open Data API and stores it in a local SQLite database for analysis and querying. The system provides temperature forecasts (max/min) for six regions across Taiwan for agricultural planning purposes.

**Goals:**
- Automatically fetch and store weather forecast data from CWA API
- Maintain historical weather forecast data in a structured database
- Provide easy-to-use query tools for data analysis
- Support agricultural weather monitoring and planning

## Tech Stack
- **Language**: Python 3.x
- **Database**: SQLite 3
- **HTTP Client**: requests library
- **Data Format**: JSON (from CWA API)
- **Standard Libraries**: json, sqlite3, datetime

## Project Conventions

### Code Style
- Follow PEP 8 style guidelines
- Use descriptive function and variable names in snake_case
- Use docstrings for all functions (Google style)
- Prefer explicit over implicit code
- Add comments for complex logic
- Use f-strings for string formatting
- Maximum line length: 100 characters

**Example:**
```python
def fetch_cwa_opendata():
    """
    Fetch weather forecast data from CWA Open Data API.
    
    Returns:
        dict: JSON response from API containing weather forecasts
    """
```

### Architecture Patterns
- **Single Responsibility**: Each function has one clear purpose
- **Data Flow**: API → Parser → Database → Query
- **Error Handling**: Use try-except blocks with specific error messages
- **Database Design**: 
  - Normalized tables with proper foreign keys
  - Track data lineage with timestamps
  - Use UNIQUE constraints to prevent duplicates
- **Separation of Concerns**:
  - `crawler.py`: Data fetching and storage
  - `query_db.py`: Data querying and analysis
  - Database layer isolated from business logic

### Testing Strategy
- Manual testing via command-line execution
- Validate API responses before processing
- Check database integrity after insertions
- Test query functions with sample data
- Verify error handling with invalid inputs

**Current Testing Approach:**
- Run crawler and verify console output
- Check database records manually
- Test query functions with different parameters

### Git Workflow
- Simple linear workflow for course assignment
- Commit messages in English or Chinese
- Descriptive commit messages explaining what was changed
- No formal branching strategy (single main development line)

## Domain Context

### Weather Data Structure
The CWA API returns agricultural weather forecasts with:
- **Locations**: 6 regions (北部地區, 中部地區, 南部地區, 東北部地區, 東部地區, 東南部地區)
- **Forecast Period**: 7-day rolling forecasts
- **Temperature Data**: Daily maximum and minimum temperatures in Celsius
- **Additional Data**: Degree-day calculations, accumulated temperature for crop growth

### Data Characteristics
- Temperature values are integers (°C)
- Dates in ISO format (YYYY-MM-DD)
- Data updates daily from CWA
- Historical data tracked via `fetched_at` timestamps

### Agricultural Context
This data is used for:
- Rice crop growth monitoring (台農67號 variety)
- Calculating growing degree-days
- Planning planting and harvesting schedules
- Regional climate comparison

## Important Constraints

### Technical Constraints
- SQLite database (file-based, single-user writes)
- API requires valid authorization token
- Network connectivity required for data fetching
- Python 3.x required
- No external database server available

### Data Constraints
- API rate limits (if any) from CWA
- 7-day forecast window only
- Data updates once per day from source
- Duplicate prevention via UNIQUE constraint

### Educational Context
- This is a course assignment (AIoT課程)
- Must be completed by specified deadline
- Code should be clear and well-documented for grading
- Self-contained project (no deployment required)

## External Dependencies

### Central Weather Administration (CWA) Open Data API
- **Endpoint**: `https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001`
- **Dataset**: F-A0010-001 (農業氣象預報-農業氣象預報資料)
- **Authorization**: Token-based (CWA-C9F8E7DB-1FAD-4DB2-BED6-54DD66994740)
- **Format**: JSON
- **Update Frequency**: Daily
- **Documentation**: https://opendata.cwa.gov.tw/

### Python Libraries
- **requests**: HTTP client for API calls
  - `pip install requests`
- **sqlite3**: Built-in Python module (no installation needed)
- **json**: Built-in Python module
- **datetime**: Built-in Python module

### Data Dependencies
- Requires active internet connection to fetch data
- API availability dependent on CWA infrastructure
- Authorization token must remain valid
