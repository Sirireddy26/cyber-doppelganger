# Cyber Doppelgänger — Security & Privacy Architecture

## Privacy Boundaries
1. **Zero Content Surveillance**: No raw keystrokes, letters, passwords, screen pixels, clipboard data, or document contents are ever collected.
2. **Derived Biometrics Only**: Only physical time intervals (dwell and flight durations) and kinematic derivatives (velocity, acceleration, curvature) are processed.
3. **Hardware Context**: Standard anonymized CPU/memory percentages via `psutil`.

## Authentication & Network Security
- Spring Security with stateless JWT authorization.
- Parametric environment variables preventing credential leakage.
- CORS restricted to registered frontend domains.
