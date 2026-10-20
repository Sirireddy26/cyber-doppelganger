# Cyber Doppelgänger — Deployment & Operations Guide
**Project:** Cyber Doppelgänger: Safe Adaptive Behavioural Identity and Continuous User Verification  
**Author/Role:** Full-Stack & ML Cybersecurity Engineer, Systems Architect  
**Version:** 1.0.0 (Production-Ready Evaluation)  
**Date:** October 2026  

---

## 1. System Architecture Overview

Cyber Doppelgänger comprises four decoupled subsystems operating in concert:
1. **Frontend Web Dashboard (Port 5173):** React 19 + TypeScript + Vite + Tailwind CSS v4 configured with the Soft Research Lab theme.
2. **Backend Application API (Port 8080):** Spring Boot 3.4 + Java 17 + Spring Security 6 (JWT) + Spring Data JPA.
3. **Machine Learning Microservice (Port 5001):** Python 3.11 + Scikit-Learn Isolation Forest detector + Safe Adaptation Engine.
4. **Desktop Telemetry Agent:** Python client monitoring OS-level user kinematic interaction and dispatching aggregated privacy-preserving timing snapshots.

---

## 2. Environment Configuration & Secrets Management

Configuration parameters are loaded through environment variables or the `.env` file. **Never commit actual credentials to version control.**

Copy the template to your environment:
```powershell
cp .env.example .env
```

### Essential Configuration Variables

| Variable | Description | Default (Dev) | Production Target |
|---|---|---|---|
| `SPRING_PROFILES_ACTIVE` | Active Spring profile | `dev` (H2 in PG mode) | `postgres` |
| `SERVER_PORT` | Backend HTTP port | `8080` | `8080` |
| `DB_HOST` | PostgreSQL hostname | `localhost` | `pg-cluster.internal` |
| `DB_PORT` | PostgreSQL port | `5432` | `5432` |
| `DB_NAME` | Database catalog name | `cyber_doppelganger` | `cyber_doppelganger` |
| `DB_USERNAME` | Database user | `sa` (H2) | `cyber_app_user` |
| `DB_PASSWORD` | Database password | `""` (H2) | `<SECURE_ROTATING_SECRET>` |
| `JWT_SECRET` | 256-bit signing key | Demo default | Minimum 64-char Hex/Base64 |
| `ML_SERVICE_URL` | Backend URL for ML | `http://localhost:5001` | `http://ml-internal:5001` |
| `VITE_API_BASE_URL` | Frontend API root | `http://localhost:8080` | `https://api.domain.edu` |

---

## 3. Database Setup: Development vs. Production

### A. Development Mode (H2 In-Memory)
- **Active Profile:** `dev`
- **URL:** `jdbc:h2:mem:cyber_doppelganger;DB_CLOSE_DELAY=-1;MODE=PostgreSQL`
- **Behavior:** Ephemeral storage, automatically initialized by JPA. No external database server required.
- **Diagnostics Badge:** Displays `H2 (In-Memory Dev DB)`.

### B. Production Mode (PostgreSQL 15+)
- **Active Profile:** `postgres`
- **URL:** `jdbc:postgresql://${DB_HOST:localhost}:${DB_PORT:5432}/${DB_NAME:cyber_doppelganger}`
- **Manual Setup Instructions:**
  ```sql
  -- Run as postgres superuser:
  CREATE DATABASE cyber_doppelganger;
  CREATE USER cyber_app_user WITH ENCRYPTED PASSWORD 'your_secure_password';
  GRANT ALL PRIVILEGES ON DATABASE cyber_doppelganger TO cyber_app_user;
  \c cyber_doppelganger
  GRANT ALL ON SCHEMA public TO cyber_app_user;
  ```
- **Schema Migration:** Apply schema definitions from `database/schema.sql`:
  ```powershell
  psql -U cyber_app_user -d cyber_doppelganger -h localhost -f database/schema.sql
  ```
- **Diagnostics Badge:** Automatically detects PostgreSQL and displays `PostgreSQL (External Relational DB)`.

---

## 4. Exact Windows PowerShell Startup Instructions

Run the subsystems in separate PowerShell terminal windows or as background processes.

### Window 1: Start Python ML Microservice (Port 5001)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\Activate.ps1
python ml/service.py
```
*Expected log:* `Cyber Doppelgänger ML Microservice started on port 5001`

### Window 2: Start Spring Boot Backend (Port 8080)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\backend"
.\mvnw.cmd spring-boot:run
```
*Expected log:* `Started CyberDoppelgangerBackendApplication in ~9.6 seconds`

### Window 3: Start React Frontend Dashboard (Port 5173)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger\frontend"
npm run dev
```
*Expected log:* `VITE v8.3.3 ready in 250 ms. Local: http://localhost:5173/`

### Window 4: Start Continuous Telemetry Agent (Optional Background Client)
```powershell
cd "c:\Users\sirir\Desktop\Cyber Doppelganger Project\cyber-doppelganger"
.\.venv\Scripts\Activate.ps1
python agent/main.py
```
*Expected log:* `Continuous monitoring active for device [local-workstation-01]`

---

## 5. Stop and Restart Procedure

### Stopping Services Gracefully
To terminate running processes in Windows PowerShell:
```powershell
# Stop by port assignment
Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 5001 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### Clean Demo Reset Procedure
If preparing for a university demonstration and resetting all synthetic data:
1. Stop the backend and Python ML microservices.
2. Reset `ml/artifacts/profile_versions.json` to the baseline `v1.0.0`:
   ```powershell
   python -c "from ml.adaptation.profile_version_manager import ProfileVersionManager; pvm = ProfileVersionManager('ml/artifacts/profile_versions.json'); pvm.unfreeze('admin', 'Pre-demo reset'); print('Reset complete.')"
   ```
3. Restart the services in order: ML (5001) &rarr; Backend (8080) &rarr; Frontend (5173).

---

## 6. Troubleshooting Guide

| Issue | Symptom | Resolution |
|---|---|---|
| Port Conflict | `Port 8080 already in use` | Check running processes: `Get-NetTCPConnection -LocalPort 8080` and stop the blocking PID. |
| ML Service Disconnected | UI reports `ML Model: OFFLINE` | Ensure `ml/service.py` is running on port 5001 and `ml/artifacts/model_isolation_forest.joblib` is present. |
| Overview Shows NONE | Trusted Profile `NONE` | Fixed in Phase B: Backend automatically synchronizes with ML baseline `v1.0.0` on diagnostic health check. |
| Database Indicator Mismatch | Overview shows H2 but Diagnostics shows PostgreSQL | Fixed in Phase C: Dynamic metadata inspection now binds to active connection properties. |
| Privacy Filter Rejection | HTTP 400 `Privacy Guard Violation` | Payload contained prohibited content keys (e.g. `typed_text`). Send only kinematic timing metrics. |
