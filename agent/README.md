# Cyber Doppelgänger — Desktop Behavioural Agent (Phase 2)
> **Safe Adaptive Behavioural Identity & Continuous User Verification**

> *"This agent is designed to collect behavioural metadata rather than user content."*

---

## 1. Purpose

The Cyber Doppelgänger Desktop Behavioural Agent runs locally on Windows and continuously observes physical user-machine interaction dynamics (keystroke rhythm, mouse kinematics, session active/idle continuity, and system process load) without recording user content.

Its primary role in the verification pipeline is to convert raw interaction timings into privacy-validated, standardized **Feature Snapshots** over periodic aggregation windows (e.g., 60 seconds).

---

## 2. Agent Architecture

```
agent/
├── collectors/
│   ├── base.py                   # Base collector interface with lifecycle contract
│   ├── keyboard/
│   │   └── keyboard_collector.py # Privacy-safe keystroke timing collector (pynput)
│   ├── mouse/
│   │   └── mouse_collector.py    # Coordinate-free mouse kinematic collector (pynput)
│   ├── application/
│   │   └── application_collector.py # Anonymous PID process context collector (psutil)
│   └── session/
│       └── session_collector.py  # Active vs. idle session duration tracker
├── features/
│   ├── keyboard_features.py      # Keystroke interval and speed derivations
│   ├── mouse_features.py         # Kinematic velocity and click statistics
│   ├── session_features.py       # Session engagement and idle ratios
│   ├── application_features.py   # Process counts and multitasking switches
│   └── feature_snapshot.py       # Central validated FeatureSnapshot model
├── privacy/
│   ├── privacy_filter.py         # Strict privacy guard rejecting sensitive fields
│   └── privacy_guard.py          # Backwards-compatible validation alias
├── buffering/
│   ├── local_buffer.py           # Thread-safe JSONL file snapshot buffer
│   └── buffer.py                 # Thread-safe transient event buffer
├── communication/
│   ├── api_client.py             # Resilient HTTP client for POST /api/agent/features
│   └── client.py                 # Backwards-compatible client alias
├── configuration/
│   ├── settings.py               # Centralized configuration dataclass
│   └── config.py                 # Backwards-compatible configuration alias
├── logging/
│   └── logger.py                 # Standardized, content-safe logging
├── tests/
│   ├── test_keyboard_features.py # Keystroke timing unit tests
│   ├── test_mouse_features.py    # Mouse kinematics unit tests
│   ├── test_session_features.py  # Session continuity unit tests
│   ├── test_privacy.py           # Explicit zero-content verification tests
│   ├── test_snapshot.py          # Schema serialization and NaN guard tests
│   ├── test_local_buffer.py      # Persistence and corruption recovery tests
│   ├── test_agent.py             # Agent foundation lifecycle tests
│   └── test_live_integration.py  # End-to-end live window test
├── main.py                       # CLI interface and main monitoring daemon
└── requirements.txt              # Agent runtime dependencies
```

---

## 3. Installation

### Prerequisites
- Python 3.11+
- Windows OS (Windows 10/11 recommended)

### Setup
From the `cyber-doppelganger/` repository root:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r agent/requirements.txt
```

---

## 4. Running the Agent

```powershell
# Normal monitoring mode (Default 60s window, local JSONL storage)
python agent/main.py

# Custom aggregation window (e.g., 10 seconds for rapid testing)
python agent/main.py --window-seconds 10

# Diagnostic health check
python agent/main.py --health

# Collector operational status
python agent/main.py --status

# Print version
python agent/main.py --version
```

Graceful termination is handled automatically upon pressing `Ctrl+C` (`SIGINT`) or system `SIGTERM`.

---

## 5. Configuration

All settings are centralized in `agent/configuration/settings.py` and can be overridden via environment variables:

| Variable | Default | Meaning |
|---|---|---|
| `AGGREGATION_WINDOW_SECONDS` | `60` | Length of sliding feature window in seconds |
| `KEYBOARD_PAUSE_THRESHOLD_SECONDS` | `1.0` | Gap between keys classified as a pause |
| `IDLE_THRESHOLD_SECONDS` | `60.0` | Inactivity threshold before session marked idle |
| `LOCAL_SNAPSHOT_STORAGE` | `true` | Persist snapshots to disk in JSON Lines |
| `SNAPSHOT_STORAGE_PATH` | `agent/data/feature_snapshots.jsonl` | Local file destination |
| `BACKEND_ENABLED` | `false` | Enable HTTP transmission to Spring Boot |
| `BACKEND_URL` | `http://localhost:8080` | Spring Boot backend base URL |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 6. Privacy Guarantees

### Privacy by Design & Zero Content Surveillance
1. **No Keystroke Content**: Keystroke callbacks capture only monotonic timestamps. Key characters, symbols, and names are discarded before memory allocation.
2. **No Screen Coordinates**: Mouse coordinates $(x, y)$ are volatile and held only in CPU registers to compute distance ($\Delta d$) and speed, then immediately overwritten.
3. **No Window or URL Surveillance**: Active application switches compare anonymous Process IDs (PIDs) using Windows API handles. Window titles, text, and browser URLs are never queried or stored.
4. **Finite Mathematical Values**: Every feature is rigorously validated against `NaN` and `Infinity`. Missing values safely default to `0.0`.

---

## 7. Backend Integration (Phase 3)

The Python agent communicates seamlessly with the Spring Boot backend via `POST /api/agent/features`.

### Integration Workflow
1. When `BACKEND_ENABLED=true`, `ApiClient` sends each aggregated `FeatureSnapshot` to the backend.
2. The payload contains `schema_version: "2.0"` and standardized timing/kinematic metadata.
3. The Spring Boot backend persists the snapshot into the `behavioural_feature_snapshots` table and responds with `HTTP 201 Created` and the generated `snapshotId`.
4. **Resilience & Local Buffering**: If the backend is offline or network fails, `ApiClient` logs the failure gracefully without crashing the agent. Snapshots remain securely in `agent/data/feature_snapshots.jsonl` via `LocalBuffer`.

### Running with Backend Forwarding
```powershell
# Enable backend forwarding
$env:BACKEND_ENABLED="true"
$env:BACKEND_URL="http://localhost:8080"
python agent/main.py --window-seconds 15
```

### Running Live E2E Integration Test
```powershell
python agent/tests/test_phase3_live_e2e.py
```
5. **Pre-Write Privacy Filter**: Every candidate snapshot is validated by `PrivacyFilter` before touching disk or network. Any occurrence of prohibited fields raises a `PrivacyViolationError` without logging the offending payload.

---

## 7. Data That Is STRICTLY NOT Collected

The desktop agent is hard-coded to **PROHIBIT** the collection or logging of:
- ❌ Typed characters, words, sentences, or keystrokes
- ❌ Passwords or credential fields
- ❌ Clipboard text, images, or files
- ❌ Screenshots, video frames, or pixel dumps
- ❌ Screen coordinates or cursor position history
- ❌ Document contents or document filenames
- ❌ Browser URLs, history, or web search queries
- ❌ Terminal commands or command-line arguments
- ❌ Personal messages, chat texts, or email bodies

---

## 8. Feature Definitions

### Keyboard Features
| Feature Name | Meaning | Unit | Calculation Method |
|---|---|---|---|
| `total_key_events` | Total keystrokes in window | Count | Number of observed press events |
| `mean_key_interval` | Average interval between consecutive presses | Seconds | Mean of $t_i - t_{i-1}$ across consecutive events |
| `median_key_interval` | Median interval between consecutive presses | Seconds | Median of sorted interval sequence |
| `key_interval_std` | Standard deviation of intervals | Seconds | Sample standard deviation of valid intervals |
| `minimum_key_interval` | Fastest transition between presses | Seconds | Minimum inter-key interval observed |
| `maximum_key_interval` | Slowest transition between presses | Seconds | Maximum inter-key interval observed |
| `typing_speed` | Event rate of keystrokes | Events/sec | `total_key_events / typing_activity_duration` (NOT words per minute) |
| `pause_count` | Number of pauses during typing | Count | Count of intervals $\ge$ `KEYBOARD_PAUSE_THRESHOLD_SECONDS` |
| `mean_pause_duration` | Average duration of typing pauses | Seconds | Mean duration of all detected pauses |
| `longest_pause` | Longest pause during typing burst | Seconds | Maximum pause duration in window |
| `typing_activity_duration` | Total active typing duration | Seconds | Total typing span minus non-active pauses |

### Mouse Features
| Feature Name | Meaning | Unit | Calculation Method |
|---|---|---|---|
| `movement_distance` | Total Euclidean cursor trajectory distance | Pixels | Accumulated $\sum \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ |
| `mean_mouse_speed` | Mean cursor velocity | Pixels/sec | Average of $\Delta d / \Delta t$ per movement segment |
| `mouse_speed_std` | Standard deviation of velocity | Pixels/sec | Standard deviation of movement velocities |
| `mean_acceleration` | Mean rate of velocity change | Pixels/sec² | Average of $\|v_i - v_{i-1}\| / \Delta t$ |
| `click_count` | Total mouse clicks in window | Count | Total recorded button click events |
| `left_click_count` | Left mouse clicks | Count | Tally of left button click events |
| `right_click_count` | Right mouse clicks | Count | Tally of right button click events |
| `middle_click_count` | Middle wheel clicks | Count | Tally of middle button click events |
| `mean_click_interval` | Average interval between clicks | Seconds | Mean of $t_{click_i} - t_{click_{i-1}}$ |
| `click_interval_std` | Standard deviation of click intervals | Seconds | Standard deviation of click intervals |
| `scroll_count` | Total scroll steps | Count | Total recorded mouse wheel events |
| `positive_scroll_count` | Upward scroll steps | Count | Count of wheel steps with $\Delta y > 0$ |
| `negative_scroll_count` | Downward scroll steps | Count | Count of wheel steps with $\Delta y < 0$ |
| `mouse_active_duration` | Active mouse movement/click time | Seconds | Accumulated movement $\Delta t$ in window |

### Session Features
| Feature Name | Meaning | Unit | Calculation Method |
|---|---|---|---|
| `session_duration` | Total elapsed monitoring time | Seconds | Time elapsed since agent start |
| `active_duration` | Total seconds of interaction in window | Seconds | $\min(W, \max(KB, MO))$ bounded by window length |
| `idle_duration` | Inactivity time within window | Seconds | $W - active\_duration$ |
| `active_idle_ratio` | Ratio of active time to idle time | Dimensionless | $active\_duration / idle\_duration$ (safe zero fallback) |
| `activity_density` | Active fraction of aggregation window | Ratio [0, 1] | $active\_duration / window\_duration$ |
| `keyboard_activity_duration`| Time spent typing | Seconds | Active keystroke time |
| `mouse_activity_duration` | Time spent using mouse | Seconds | Active mouse time |

### Application Features
| Feature Name | Meaning | Unit | Calculation Method |
|---|---|---|---|
| `process_count` | Total processes running on system | Count | Size of `psutil.pids()` |
| `active_process_count` | Processes currently running/active | Count | Active CPU scheduling process tally |
| `application_switch_count` | Frequency of foreground PID switches | Count | Count of anonymous PID changes in active window |
| `process_activity_count` | Process checks during window | Count | Number of background monitor checks |
| `application_activity_duration`| Total application interaction time | Seconds | Active foreground interaction duration |

---

## 9. Automated Testing

Run the full agent test suite with:

```powershell
python -m unittest discover -s agent/tests
```

### Test Coverage Highlights:
- **`test_keyboard_features.py`**: Zero events, single event, normal typing cadence, pause detection, clock skews, NaN/inf guards.
- **`test_mouse_features.py`**: Movement kinematics, zero-dt protection, left/right/middle click counts, scroll counting.
- **`test_session_features.py`**: Active/idle duration breakdown, ratio calculation, zero-length safety.
- **`test_privacy.py`**: Enforces that stimulated keystrokes ('A', 'SecretPass') never appear in snapshots or logs; validates prohibited fields rejection.
- **`test_snapshot.py`**: Validates JSON schema, bidirectional serialization, and non-finite number sanitization.
- **`test_local_buffer.py`**: Verifies JSONL snapshot persistence, reading pending items, and recovering from corrupted lines.
- **`test_live_integration.py`**: Spins up live background listeners, records a live window, and checks disk persistence.

---

## 10. Known Limitations

- **Headless Environments**: When running in headless virtualized containers without a desktop session, `pynput` input hooks may not receive hardware events. The agent handles this gracefully with warning state reporting.
- **Elevated Window Hooks**: Keystroke monitoring in Windows User Account Control (UAC) elevated windows requires administrator privileges for the Python interpreter to receive low-level hooks.

---

## 11. Future Connection to Backend

In later phases, the local buffer will feed the Spring Boot continuous verification endpoint:

```
POST /api/agent/features
Content-Type: application/json
```

When `BACKEND_ENABLED=true`, the `ApiClient` will stream buffered snapshots while continuing to buffer locally if connection drops.
