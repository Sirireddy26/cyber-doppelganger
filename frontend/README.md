# Cyber Doppelgänger — React Frontend Dashboard (Phase 1)

Modern web dashboard for the Cyber Doppelgänger continuous user verification system.

---

## 1. Technologies

- **React 19 & TypeScript**
- **Vite**: Ultra-fast development and optimized production bundling
- **Tailwind CSS v4**: Restrained, professional cybersecurity styling
- **Lucide React**: Clean interface iconography
- **Recharts**: Prepared for behavioral kinematic visualization (Phase 2+)

---

## 2. Configuration & API Service

API requests are managed centrally in `src/services/api.ts`.
Configure the backend target using environment variables:

```bash
# In .env (or copy from .env.example)
VITE_API_BASE_URL=http://localhost:8080
```

---

## 3. Running Locally

```powershell
# Install dependencies
npm install

# Start Vite dev server (runs on http://localhost:5173)
npm run dev

# Build production bundle
npm run build
```

---

## 4. Phase 1 Implementation Notes

- **Real Health Communication**: Queries `GET /api/health` directly through `ApiService` and displays genuine server status.
- **No Fake Metrics**: Displays clear empty state ("Waiting for behavioural data") rather than simulated metrics or fabricated confidence numbers.
- **Design Restraint**: Adheres to research-grade visual standards, avoiding hacker clichés, skull graphics, and unnecessary visual noise.
