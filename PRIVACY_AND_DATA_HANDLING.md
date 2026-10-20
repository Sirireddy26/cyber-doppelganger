# Cyber Doppelgänger — Privacy Specification & Data Handling Policy
**Project:** Cyber Doppelgänger: Safe Adaptive Behavioural Identity and Continuous User Verification  
**Author/Role:** Cybersecurity & Privacy Engineer, Research Software Specialist  
**Standard Compliance:** Privacy by Design, Ethical Human-Computer Interaction Research  
**Date:** October 2026  

---

## 1. Ethical Research Mandate & Zero-Content Non-Surveillance Policy

Cyber Doppelgänger is designed to evaluate continuous identity verification strictly without surveillance. The platform operates under an immutable architectural boundary: **zero storage, transmission, or inference over content**.

The system treats keystroke timings and mouse movement dynamics purely as biomechanical kinematic signals. At no point in the software lifecycle are typed words, passwords, clipboard contents, screen pixels, or browsing trails intercepted or stored.

---

## 2. Definitive Data Boundaries

### A. Strictly Prohibited Data Categories (Never Collected)

The following data categories are prohibited by runtime software filters (`PrivacyFilter.java` and `privacy_filter.py`). Any payload containing these keys or contents is rejected with an HTTP 400 Privacy Violation exception:

1. **Typed Characters & Text:** No individual key characters (`char`, `key_name`, `key_char`), words, sentences, or phrases.
2. **Authentication Secrets:** No passwords, PINs, tokens, MFA secrets, or credential fields.
3. **Clipboard Data:** No clipboard text, copied buffers, or paste history.
4. **Display & Visual Content:** No screenshots, screen captures, framebuffer buffers, window titles, or UI labels.
5. **Browsing & Document Metadata:** No URLs, browser histories, file names, document contents, or application window titles.
6. **Continuous Raw Coordinate Trails:** No persistent recording of full absolute spatial coordinate traces.

### B. Permitted Privacy-Safe Feature Summaries

Only aggregated statistical summaries over fixed observation windows (e.g., 60 seconds) are collected:

| Permitted Metric | Units | Description & Scientific Purpose |
|---|---|---|
| `mean_dwell_time_ms` | Milliseconds (ms) | Average duration a physical key is held depressed. Reflects finger pressure and mechanical switch cadence. |
| `mean_flight_time_ms` | Milliseconds (ms) | Average latency between releasing one key and striking the next. Measures cognitive motor transition fluidity. |
| `typing_speed_wpm` | Words Per Minute | Keystroke rate calculated as `(Keystrokes / 5) / minutes`. Reflects typing rhythm. |
| `backspace_rate` | Ratio ($[0, 1]$) | Proportion of backspace keystrokes to total keystrokes. Measures motor error correction rate. |
| `mean_mouse_speed` | Pixels/second | Mean cursor displacement rate over motion vectors. |
| `mean_acceleration` | Pixels/second² | Rate of velocity change during cursor movement. Distinguishes ballistic flicks from targeted motion. |
| `mouse_jitter` | Unitless index | Normalized speed standard deviation ($\sigma / (\mu + 1)$). Measures micro-tremors and hesitations. |
| `movement_efficiency` | Ratio ($[0, 1]$) | Euclidean straight-line distance divided by trajectory distance. Measures curvature. |
| `idle_ratio` | Ratio ($[0, 1]$) | Ratio of inactivity to total session window duration. |

---

## 3. Data Processing Lifecycle & Retention Boundaries

```
[User Interaction]
       │
       ▼ (Keystroke & Mouse OS Hooks)
[In-Memory Feature Extractor] ───> Discards characters immediately
       │
       ▼ (Aggregated Kinematics Only)
[Client-Side Privacy Filter] ───> Verifies absence of forbidden keys
       │
       ▼ (HTTP POST /api/agent/features)
[Backend Privacy Filter Guard] ──> Validates JSON tree recursively
       │
       ▼
[PostgreSQL / H2 Database] ──────> Stores only numerical summaries
       │
       ▼ (JSON payload over private loopback)
[Isolation Forest Model] ────────> Computes decision score & updates candidate buffer
```

### Retention Schedule
- **Observation Snapshots:** Retained for the duration of the evaluation session or benchmark trial. Default retention: 30 days maximum.
- **Trained Profiles:** Reference centroids and covariance summaries representing `v1.0.0` through `vX.Y.Z` are retained until an administrative profile reset.
- **Audit Logs:** Immutable audit entries (action, timestamp, operator, outcome) retained for accountability.

---

## 4. User Consent & Documented Deletion Procedure

### A. Interactive Consent & Collection Control
- Users can stop desktop telemetry at any time by stopping the background process (`Ctrl+C` in the agent terminal).
- The web playground provides a persistent **Reset Arena** button that flushes all in-memory buffers immediately.

### B. Documented Data Deletion Procedure
To wipe all stored research telemetry and reset identity profiles:
```powershell
# 1. Purge all stored feature snapshots and verification records from database
psql -U cyber_app_user -d cyber_doppelganger -c "TRUNCATE behavioural_feature_snapshots, verification_results, adaptation_events, profile_freeze_records CASCADE;"

# 2. Reset Python ML profile version lineage to clean baseline
python -c "from ml.adaptation.profile_version_manager import ProfileVersionManager; pvm = ProfileVersionManager('ml/artifacts/profile_versions.json'); pvm.unfreeze('admin', 'Manual privacy purge'); print('Privacy purge complete.')"
```

---

## 5. Automated Verification Test Suite

Privacy boundary guarantees are validated by automated continuous integration tests in `tests/test_privacy_boundary.py`. The suite asserts that identifiable strings (`SUPER_SECRET_PASSWORD_123`, `CRITICAL_SECRET_CREDENTIAL_DO_NOT_STORE`) are:
1. Rejected at the agent level before dispatch.
2. Rejected at the API gateway with HTTP 400.
3. Excluded from error responses, database records, and export files.
