## ADDED Requirements

### Requirement: Web-Based Temperature Visualization
The system SHALL provide a web-based user interface for visualizing weather temperature forecasts with interactive controls and charts.

#### Scenario: Launch web application
- **WHEN** user runs `streamlit run streamlit_app.py`
- **THEN** web application SHALL start on port 8501
- **AND** browser SHALL open automatically
- **AND** main page SHALL display temperature data

#### Scenario: View all locations overview
- **WHEN** user accesses the web application
- **THEN** overview page SHALL display temperature data for all locations
- **AND** summary statistics SHALL be shown
- **AND** last update timestamp SHALL be visible

### Requirement: Interactive Location Selection
The system SHALL provide a dropdown selector allowing users to filter temperature data by specific geographic location.

#### Scenario: Select location from dropdown
- **WHEN** user opens location dropdown
- **THEN** all 6 regions SHALL be listed (北部地區, 中部地區, 南部地區, 東北部地區, 東部地區, 東南部地區)
- **AND** "All Locations" option SHALL be available
- **WHEN** user selects a location
- **THEN** data SHALL update to show only that location

#### Scenario: Default location selection
- **WHEN** user first loads the page
- **THEN** "All Locations" SHALL be selected by default
- **AND** data for all regions SHALL be displayed

### Requirement: Temperature Trend Visualization
The system SHALL display temperature forecasts as interactive line charts showing both maximum and minimum temperature trends over time.

#### Scenario: Display temperature line chart
- **WHEN** location is selected
- **THEN** line chart SHALL show forecast dates on X-axis
- **AND** temperature values on Y-axis
- **AND** two lines SHALL be displayed (MaxT and MinT)
- **AND** lines SHALL be color-coded (red for max, blue for min)
- **AND** chart SHALL be interactive (hover for details)

#### Scenario: Multi-location comparison
- **WHEN** "All Locations" is selected
- **THEN** chart SHALL show temperature trends for all regions
- **AND** each location SHALL have distinct color
- **OR** multiple charts SHALL be displayed per location

### Requirement: Data Table Display
The system SHALL display detailed temperature forecast data in tabular format with sorting capabilities.

#### Scenario: Show forecast table
- **WHEN** user views selected location
- **THEN** table SHALL display columns: Location, Date, Max Temp, Min Temp
- **AND** data SHALL be sorted by date (ascending)
- **AND** temperature values SHALL include unit (°C)

#### Scenario: Table interactivity
- **WHEN** user clicks column header
- **THEN** table SHALL sort by that column
- **AND** sort direction SHALL toggle (asc/desc)

### Requirement: Summary Statistics Display
The system SHALL calculate and display summary statistics for temperature data including average, minimum, and maximum values.

#### Scenario: Display statistics metrics
- **WHEN** location is selected
- **THEN** metrics SHALL show average max temperature
- **AND** average min temperature
- **AND** highest recorded max temperature
- **AND** lowest recorded min temperature
- **AND** temperature range
- **AND** number of forecast days

#### Scenario: Statistics update on selection
- **WHEN** user changes location selection
- **THEN** statistics SHALL recalculate immediately
- **AND** updated values SHALL display within 1 second

### Requirement: Database Connection and Error Handling
The system SHALL connect to SQLite database and handle missing or corrupted data gracefully with clear user feedback.

#### Scenario: Successful database connection
- **WHEN** streamlit app starts
- **AND** sqlitedata.db exists
- **THEN** data SHALL load successfully
- **AND** application SHALL display normally

#### Scenario: Missing database file
- **WHEN** streamlit app starts
- **AND** sqlitedata.db does not exist
- **THEN** error message SHALL display clearly
- **AND** instructions to run crawler.py SHALL be shown
- **AND** application SHALL not crash

#### Scenario: Empty database
- **WHEN** database exists but has no records
- **THEN** message SHALL inform user "No data available"
- **AND** suggest running crawler to fetch data
- **AND** application SHALL remain functional

### Requirement: Data Freshness Indicator
The system SHALL display when data was last fetched from the API to help users understand data currency.

#### Scenario: Display last update time
- **WHEN** data is loaded from database
- **THEN** most recent fetch timestamp SHALL be displayed
- **AND** format SHALL be human-readable (e.g., "Last updated: 2025-12-06 15:57")

#### Scenario: Highlight stale data
- **WHEN** last fetch was more than 24 hours ago
- **THEN** warning indicator SHALL be shown
- **AND** suggest running crawler to update data

### Requirement: Responsive Layout
The system SHALL provide a responsive layout that works on desktop and mobile devices.

#### Scenario: Desktop view
- **WHEN** accessed on desktop browser
- **THEN** sidebar SHALL show on left
- **AND** charts SHALL use full width
- **AND** all controls SHALL be easily accessible

#### Scenario: Mobile view
- **WHEN** accessed on mobile device
- **THEN** layout SHALL adapt to narrow screen
- **AND** sidebar SHALL collapse/expand
- **AND** charts SHALL remain readable
- **AND** tables SHALL scroll horizontally if needed
