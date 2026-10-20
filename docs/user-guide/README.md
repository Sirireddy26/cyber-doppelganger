# Cyber Doppelgänger — User & Developer Guide

## Quick Start (Phase 1)

1. **Start the Backend**:
   ```powershell
   cd backend
   .\mvnw.cmd spring-boot:run
   ```
2. **Start the Frontend**:
   ```powershell
   cd frontend
   npm run dev
   ```
3. **Verify the Agent**:
   ```powershell
   python agent/main.py --health
   ```
4. **Run End-to-End Test Suite**:
   ```powershell
   cd scripts
   .\verify-all.bat
   ```
