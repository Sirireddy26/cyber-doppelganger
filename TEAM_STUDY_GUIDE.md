# Cyber Doppelgänger — Team Study Material & Architecture Handbook

> 💡 **Full Study Guide Available:**  
> The comprehensive, beginner-friendly study guide for teammates is located at [`docs/TEAM_STUDY_GUIDE.md`](docs/TEAM_STUDY_GUIDE.md).

---

## 📌 Executive Cheat Sheet for Teammates

### 1. What is Cyber Doppelgänger in 1 Sentence?
A continuous behavioural biometrics authentication system that verifies whether the legitimate user is sitting at the keyboard purely by **how** they type and move their mouse, **without ever recording what they type or do (zero-content surveillance).**

### 2. The 4 Decoupled Subsystems

| Subsystem | Tech Stack | Port / Location | Primary Role |
| :--- | :--- | :--- | :--- |
| **Desktop Agent** | Python 3.11 | `agent/main.py` | Runs locally in background; calculates 60-second interaction statistics; strictly drops keys, coordinates, and URLs. |
| **Backend API** | Java 17, Spring Boot 3.4.4 | `http://localhost:8080` | Handles snapshot ingestion, replay defense, device auto-registration, Flyway migrations, and database persistence (H2/PostgreSQL). |
| **ML Microservice** | Python, Flask, Scikit-learn | `http://localhost:5001` | Runs 12D Isolation Forest anomaly detection (threshold: `+0.0327`), candidate buffering, and drift evaluation. |
| **Frontend UI** | React 19, TypeScript, Vite | `http://localhost:5173` | Dark-mode security operations console with Biometric Playground, live anomaly diagnostics, and profile freeze/unfreeze controls. |

### 3. How to Run Everything on Your Machine

```powershell
# Terminal 1: Python ML Microservice (Port 5001)
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\python.exe ml/service.py

# Terminal 2: Java Spring Boot Backend (Port 8080)
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\backend"
.\mvnw.cmd spring-boot:run

# Terminal 3: React Frontend Dashboard (Port 5173)
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\frontend"
npm run dev

# Terminal 4: Desktop Agent (Telemetry Ingestion)
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
$env:BACKEND_ENABLED="true"
$env:BACKEND_URL="http://localhost:8080"
$env:DEVICE_ID="teammate-workstation-01"
.\.venv\Scripts\python.exe agent/main.py
```

### 4. Verification & Testing Proof
- **Total Tests:** 109 automated tests passing across the repository (33 Agent, 42 ML, 4 Privacy, 30 Backend).
- **Audit Results:** See [`LOCAL_VERIFICATION_RESULTS.md`](LOCAL_VERIFICATION_RESULTS.md) for actual test outputs and database records.

---
📖 **Read the full study guide with diagrams, math intuition, and Viva/Defense Q&A in [`docs/TEAM_STUDY_GUIDE.md`](docs/TEAM_STUDY_GUIDE.md).**
