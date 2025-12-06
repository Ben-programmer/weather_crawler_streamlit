## ADDED Requirements

### Requirement: Scheduled Execution Mode
The system SHALL support automated scheduled execution of the weather data crawler at user-configured intervals without manual intervention.

#### Scenario: Daily scheduled run at specific time
- **WHEN** scheduler is configured for daily execution at 08:00
- **AND** scheduler process is running
- **THEN** crawler SHALL execute automatically at 08:00 each day
- **AND** execution results SHALL be logged

#### Scenario: Hourly interval execution
- **WHEN** scheduler is configured for hourly intervals
- **AND** scheduler process is running
- **THEN** crawler SHALL execute once per hour
- **AND** each execution SHALL be independent

#### Scenario: Custom interval execution
- **WHEN** scheduler is configured with custom interval (e.g., every 6 hours)
- **AND** scheduler process is running
- **THEN** crawler SHALL execute at the specified interval
- **AND** timing SHALL be consistent across executions

### Requirement: Configuration Management
The system SHALL support flexible configuration of scheduling parameters through YAML files and command-line arguments.

#### Scenario: Load configuration from YAML file
- **WHEN** scheduler starts with valid config.yaml
- **THEN** schedule settings SHALL be loaded from file
- **AND** invalid settings SHALL trigger validation errors with clear messages

#### Scenario: Override config with command-line arguments
- **WHEN** scheduler is started with CLI arguments (e.g., --time 10:00)
- **THEN** CLI arguments SHALL override config.yaml settings
- **AND** final configuration SHALL be logged for verification

#### Scenario: Missing or invalid configuration
- **WHEN** config.yaml is missing or contains invalid values
- **THEN** scheduler SHALL use sensible defaults
- **OR** exit with clear error message for critical settings
- **AND** list all configuration issues found

### Requirement: Process Lock Management
The system SHALL prevent multiple scheduler instances from running simultaneously to avoid database conflicts and duplicate data collection.

#### Scenario: First scheduler instance starts successfully
- **WHEN** no scheduler is currently running
- **AND** new scheduler process starts
- **THEN** PID lock file SHALL be created
- **AND** scheduler SHALL begin scheduled operations

#### Scenario: Prevent duplicate scheduler instances
- **WHEN** scheduler process is already running
- **AND** user attempts to start second instance
- **THEN** new instance SHALL detect existing lock
- **AND** exit with clear message about running instance
- **AND** display PID of running scheduler

#### Scenario: Cleanup stale lock file
- **WHEN** PID lock file exists from crashed process
- **AND** process ID is not active
- **THEN** stale lock SHALL be removed automatically
- **AND** new scheduler SHALL start successfully

### Requirement: Error Handling and Retry Logic
The system SHALL handle transient failures gracefully with automatic retry mechanisms and appropriate backoff strategies.

#### Scenario: Successful crawler execution
- **WHEN** scheduled crawler run executes
- **AND** API call succeeds
- **AND** database write succeeds
- **THEN** success SHALL be logged
- **AND** next run SHALL be scheduled normally

#### Scenario: Network failure with retry
- **WHEN** scheduled crawler run fails due to network error
- **AND** retry attempts remain
- **THEN** system SHALL wait for backoff period
- **AND** retry crawler execution
- **AND** log each retry attempt

#### Scenario: Permanent failure after max retries
- **WHEN** crawler fails for max retry attempts
- **AND** all retry attempts exhausted
- **THEN** failure SHALL be logged with full error details
- **AND** system SHALL continue to next scheduled run
- **AND** failed run SHALL be recorded in fetch_log table

#### Scenario: Database lock error handling
- **WHEN** database is locked by another process
- **THEN** system SHALL wait and retry with exponential backoff
- **AND** log database lock condition
- **AND** eventually succeed or log final failure

### Requirement: Comprehensive Logging
The system SHALL provide detailed logging of all scheduled operations, execution results, and errors to both console and rotating log files.

#### Scenario: Dual output logging
- **WHEN** scheduler is running
- **THEN** logs SHALL be written to console (stdout)
- **AND** simultaneously written to log file
- **AND** both outputs SHALL contain identical information

#### Scenario: Log file rotation
- **WHEN** log file exceeds configured size limit (e.g., 10 MB)
- **THEN** current log file SHALL be rotated/archived
- **AND** new log file SHALL be created
- **AND** old log files SHALL be retained according to retention policy

#### Scenario: Structured log entries
- **WHEN** any logging occurs
- **THEN** log entries SHALL include timestamp
- **AND** log level (INFO, WARNING, ERROR)
- **AND** clear message describing the event
- **AND** relevant context (e.g., record count, error details)

#### Scenario: Startup and shutdown logging
- **WHEN** scheduler starts
- **THEN** log configuration details and schedule
- **WHEN** scheduler receives shutdown signal
- **THEN** log graceful shutdown initiation and cleanup

### Requirement: Graceful Shutdown
The system SHALL support clean shutdown on user interrupt signals, ensuring proper resource cleanup and state consistency.

#### Scenario: SIGINT (Ctrl+C) handling
- **WHEN** scheduler receives SIGINT signal
- **THEN** current operation SHALL complete if possible
- **AND** PID lock file SHALL be removed
- **AND** resources SHALL be released
- **AND** exit with status 0

#### Scenario: SIGTERM handling
- **WHEN** scheduler receives SIGTERM signal (e.g., from systemctl stop)
- **THEN** graceful shutdown sequence SHALL execute
- **AND** cleanup SHALL be identical to SIGINT handling

#### Scenario: Shutdown during active crawler run
- **WHEN** shutdown signal received during crawler execution
- **THEN** system SHALL wait for crawler to complete (with timeout)
- **OR** allow crawler subprocess to continue and detach
- **AND** clean up scheduler resources
- **AND** log interrupted state

## MODIFIED Requirements

### Requirement: Weather Data Collection
The system SHALL fetch weather forecast data from CWA Open Data API and store it in a SQLite database. **[MODIFIED to support scheduled execution mode]**

#### Scenario: Manual execution (existing)
- **WHEN** user runs `python crawler.py` directly
- **THEN** data SHALL be fetched immediately
- **AND** results SHALL be displayed to console
- **AND** database SHALL be updated

#### Scenario: Scheduled execution (new)
- **WHEN** crawler is invoked by scheduler process
- **THEN** data SHALL be fetched automatically
- **AND** results SHALL be logged (not displayed to console)
- **AND** database SHALL be updated
- **AND** execution status SHALL be returned to scheduler

#### Scenario: Return execution status
- **WHEN** crawler execution completes
- **THEN** function SHALL return success/failure status
- **AND** include error details if failed
- **AND** scheduler can use status for retry logic
