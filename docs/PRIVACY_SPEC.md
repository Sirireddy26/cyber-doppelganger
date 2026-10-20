# Cyber Doppelgänger Privacy Specification

## Non-Negotiable Privacy Guarantees

In accordance with strict ethical standards, GDPR/privacy regulations, and research validity requirements, the Cyber Doppelgänger system operates under an immutable zero-content surveillance policy.

### Strictly Prohibited Data
The agent and pipeline are physically and architecturally barred from collecting, processing, storing, or transmitting:
1. **Actual Typed Characters / Keystroke Logs**: Never records alphabetical, numerical, symbol, or control key values.
2. **Passwords & Sensitive Credentials**: No form, field, or password input text is captured.
3. **Chat & Message Contents**: No communication text or messaging application data is inspected.
4. **Clipboard Contents**: No copy/paste data, text, or file buffers are inspected or read.
5. **Screenshots & Video Capture**: No pixel captures, screen recordings, or frame buffers.
6. **Screen & Document Contents**: No OCR, DOM inspection, or document text reading.
7. **Browser URLs & History**: No visited URLs, browser tabs, or search queries.

---

### Permitted Behavioral Biometrics Only
Only derived statistical timing intervals and physical movement dynamics are captured:

| Metric Category | Permitted Features | Mathematical Representation |
|-----------------|-------------------|-----------------------------|
| **Keystroke Dynamics** | Dwell Time | $t_{release} - t_{press}$ |
| | Flight Time | $t_{press_{i+1}} - t_{release_i}$ |
| | Press Latency | $t_{press_{i+1}} - t_{press_i}$ |
| **Mouse Kinematics** | Velocity | $\Delta \text{distance} / \Delta t$ |
| | Acceleration | $\Delta v / \Delta t$ |
| | Curvature / Tortuosity | Path length / Euclidean distance |
| | Click Duration | $t_{click\_release} - t_{click\_press}$ |
| **System Context** | CPU & Memory Percent | Anonymized hardware utilization context |

---

### Enforcement Mechanisms
- `PrivacyGuard` runtime filter validates each event before buffering.
- Memory references are discarded immediately upon timestamp calculation.
- Feature vectors are purely mathematical floating-point aggregates.
