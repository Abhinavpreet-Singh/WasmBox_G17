# Frontend structure

WasmBox dashboard — StreamForge-style layout, WasmBox pages.

## Folder layout

```
frontend/src/
├── App.jsx                 # Page switcher from sidebar
├── main.jsx
├── index.css               # CSS variables (--wb-*) for future theme
│
├── config/
│   └── navigation.js       # Sidebar items (6 pages)
│
├── context/
│   ├── AppContext.js
│   └── AppProvider.jsx     # health, tenant, executions stub
│
├── hooks/
│   └── useApp.js
│
├── lib/
│   ├── api.js
│   └── observability.js    # Grafana :3002, Prometheus :9091
│
├── components/
│   └── layout/             # AppShell, Sidebar, AppHeader, PageLayout
│
└── pages/
    ├── Overview.jsx
    ├── Playground.jsx      # Monaco + Run (Week 1 Day 5)
    ├── Plugins.jsx         # Week 3
    ├── SecurityLab.jsx     # Week 3
    ├── Operations.jsx      # Week 4
    └── Metrics.jsx         # Week 4
```

## Routing

No `react-router` — `activePage` in `App.jsx` swaps the page. Use `navigateTo('playground')` from `useApp()` for CTAs.

## Shared state — `useApp()`

`apiHealth`, `tenantId`, `executions`, `wsStatus`, `navigateTo`. WebSocket wiring lands Week 2 Day 9.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

API must be on `http://localhost:8001`.
