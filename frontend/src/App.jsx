import { useState } from 'react';
import { AppProvider } from './context/AppProvider';
import AppShell from './components/layout/AppShell';
import { NAV_ITEMS, DEFAULT_PAGE } from './config/navigation';

import Overview from './pages/Overview';
import Playground from './pages/Playground';
import Plugins from './pages/Plugins';
import SecurityLab from './pages/SecurityLab';
import Operations from './pages/Operations';
import Metrics from './pages/Metrics';

const PAGES = {
  overview: Overview,
  playground: Playground,
  plugins: Plugins,
  security: SecurityLab,
  operations: Operations,
  metrics: Metrics,
};

export default function App() {
  const [activePage, setActivePage] = useState(DEFAULT_PAGE);

  const ActivePageComponent = PAGES[activePage] ?? PAGES[NAV_ITEMS[0].id];

  return (
    <AppProvider navigateTo={setActivePage}>
      <AppShell activePage={activePage} onNavigate={setActivePage}>
        <ActivePageComponent />
      </AppShell>
    </AppProvider>
  );
}
