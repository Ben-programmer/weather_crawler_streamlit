# Design: Scheduled Crawler System

## Context
The current weather crawler requires manual execution. To support automated data collection for continuous monitoring, we need a scheduling system that runs the crawler at configured intervals while handling errors, preventing duplicate runs, and providing visibility through logging.

**Constraints:**
- Must work cross-platform (Windows, macOS, Linux)
- Should be simple enough for educational purposes
- Cannot rely on external services or databases for scheduling
- Must handle network failures gracefully

**Stakeholders:**
- Students learning about automated data collection
- Users wanting continuous weather monitoring
- System administrators deploying the solution

## Goals / Non-Goals

**Goals:**
- Automated execution at configurable intervals
- Simple configuration (YAML or command-line)
- Graceful error handling and retry logic
- Prevention of multiple concurrent instances
- Clear logging for debugging and monitoring
- Cross-platform compatibility

**Non-Goals:**
- Distributed scheduling across multiple machines
- Web UI for schedule management
- Complex job queuing or priority systems
- Database-backed scheduling state
- Monitoring dashboards or alerting systems

## Decisions

### Decision 1: Use `schedule` Library
**What:** Use Python `schedule` library for in-process scheduling

**Why:**
- Lightweight and simple to understand
- Pure Python, cross-platform
- Suitable for single-machine use case
- Easy to teach in educational context
- No external daemon required

**Alternatives Considered:**
- **APScheduler**: More features but heavier, complex API
- **System cron/Task Scheduler**: Platform-specific, harder to configure
- **Celery**: Requires message broker, massive overkill

### Decision 2: Configuration via YAML + CLI
**What:** Primary config in `config.yaml`, overrideable via CLI args

**Why:**
- YAML is human-readable and easy to edit
- CLI args allow quick testing without file edits
- Separation of defaults and overrides

**Example:**
```yaml
schedule:
  type: daily  # daily, hourly, interval
  time: "08:00"  # 24-hour format
  interval_minutes: 60  # if type is 'interval'

retry:
  max_attempts: 3
  backoff_seconds: 60

logging:
  level: INFO
  file: logs/scheduler.log
  max_size_mb: 10
```

### Decision 3: Process Lock via PID File
**What:** Use PID file to prevent multiple scheduler instances

**Why:**
- Simple and effective for single-machine scenario
- Cross-platform compatible
- Easy to implement and debug
- Allows manual cleanup if needed

**Implementation:**
```python
# Create .scheduler.pid file on start
# Check if PID is still running
# Clean up on graceful shutdown
```

### Decision 4: Logging to File + Console
**What:** Dual logging to both console and rotating file

**Why:**
- Console output for interactive testing
- File logs for production/background runs
- Rotation prevents disk space issues
- Timestamps for troubleshooting

**Format:**
```
2025-12-06 08:00:01 [INFO] Starting scheduled crawler run
2025-12-06 08:00:15 [SUCCESS] Fetched 42 records from CWA API
2025-12-06 08:00:16 [SUCCESS] Saved 42 records to database
```

## Architecture

### Component Structure
```
scheduler.py (main)
├── Config Loading (config.yaml + CLI args)
├── Process Lock Manager (PID file)
├── Schedule Registration (schedule library)
├── Job Executor (calls crawler.py)
├── Error Handler (retry logic)
└── Logger (console + file)
```

### Data Flow
```
1. scheduler.py starts
2. Load config
3. Check/create PID lock
4. Register scheduled job
5. Enter schedule loop
6. [At scheduled time]
   ├── Execute crawler.py
   ├── Capture output/errors
   ├── Log results
   └── Handle failures (retry)
7. On signal (Ctrl+C)
   ├── Cleanup PID file
   └── Graceful exit
```

### Error Handling Strategy
```python
def run_crawler_with_retry():
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_crawler()
            if result.success:
                log_success()
                return
            else:
                log_warning(attempt)
        except NetworkError:
            if attempt < max_attempts:
                sleep(backoff_seconds * attempt)
                continue
            else:
                log_failure()
                send_notification()  # future enhancement
```

## Integration Points

### With crawler.py
- Import and call `fetch_cwa_opendata()` as library function
- OR use subprocess to run as separate process (simpler, more isolated)
- Return success/failure status code

### With database
- No changes needed
- Crawler handles all DB operations
- Scheduler just invokes crawler

### With filesystem
- Read: `config.yaml`
- Write: `.scheduler.pid`, `logs/scheduler.log`

## Risks / Trade-offs

### Risk 1: In-Memory Scheduling State
**Risk:** If scheduler process crashes, no automatic restart
**Mitigation:** 
- Document use of system services (systemd, launchd) for auto-restart
- Provide example service files
**Trade-off:** Simplicity over robustness (acceptable for educational project)

### Risk 2: Time Zone Handling
**Risk:** Confusion about local vs UTC time
**Mitigation:**
- Use local time by default (more intuitive)
- Document clearly in config
- Add timezone parameter for future enhancement
**Trade-off:** Simplicity over precision (acceptable for single-location use)

### Risk 3: Long-Running Process
**Risk:** Memory leaks, resource accumulation over time
**Mitigation:**
- Keep scheduler logic minimal
- Use subprocess for crawler (isolates resources)
- Document restart schedule (e.g., weekly)
**Trade-off:** Simplicity over perfect resource management

## Migration Plan

### Phase 1: Additive Deployment
1. Add new files (`scheduler.py`, `config.yaml`)
2. Install new dependencies (`schedule`, `pyyaml`)
3. Existing `crawler.py` continues to work standalone
4. No data migration needed

### Phase 2: User Adoption (Optional)
1. Users can choose to adopt scheduler
2. Existing cron jobs can be migrated
3. No forced migration

### Rollback
- Delete new files
- Uninstall new dependencies
- Revert to manual execution
- No data loss risk

## Performance Considerations

**Expected Load:**
- One crawler run per day = minimal CPU/memory
- Each run: ~1-2 seconds network, <1 second DB write
- Scheduler overhead: <10 MB RAM, negligible CPU
- Log file: ~1 KB per run = ~365 KB per year

**Scalability:**
Not a concern for this use case. Single machine, single user, low frequency.

## Security Considerations

1. **API Token Security:**
   - Token currently hardcoded in `crawler.py`
   - Future: Move to environment variable or secure config
   - Not addressed in this change (separate concern)

2. **File Permissions:**
   - Config file should be user-readable only
   - PID file and logs in user directory
   - No elevated privileges needed

3. **Process Isolation:**
   - Scheduler runs as normal user
   - No network listening/exposed ports
   - Low security risk profile

## Testing Strategy

### Unit Tests (Optional for v1)
- Config loading and validation
- PID lock creation/cleanup
- Schedule parsing

### Integration Tests
1. Start scheduler, verify it waits
2. Trigger immediate run, verify crawler executes
3. Send SIGINT, verify graceful shutdown
4. Start second instance, verify rejection (PID lock)
5. Simulate API failure, verify retry logic
6. Check log file creation and content

### Manual Tests
1. Run for 24 hours, verify daily execution
2. Test on Windows, macOS, Linux
3. Test with various config options
4. Test error scenarios (network down, disk full)

## Open Questions

1. **Q:** Should scheduler support multiple schedules (e.g., hourly + daily)?
   **A:** No, keep simple. Single schedule per instance. Run multiple instances if needed.

2. **Q:** Should we add email notifications on failure?
   **A:** No for v1. Add to future enhancements. Keep dependencies minimal.

3. **Q:** How to handle DST transitions?
   **A:** Accept Python's default behavior. Not critical for this use case.

4. **Q:** Should we support cron syntax?
   **A:** No, use simple config options. Cron syntax adds complexity.

## Future Enhancements (Not in Scope)

- Web dashboard for viewing schedule and logs
- Email/SMS notifications on failures
- Multiple schedule profiles
- Dynamic schedule changes without restart
- Distributed scheduling across multiple machines
- Integration with monitoring systems (Prometheus, etc.)
