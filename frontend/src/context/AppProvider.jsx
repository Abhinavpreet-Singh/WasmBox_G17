import { useCallback, useEffect, useMemo, useState } from 'react';
import { AppContext } from './AppContext';
import { apiGet } from '../lib/api';

export function AppProvider({ navigateTo, children }) {
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [apiHealth, setApiHealth] = useState(null);
  const [tenantId, setTenantId] = useState('tenant_a');
  const [executions, setExecutions] = useState([]);
  const [playgroundSource, setPlaygroundSource] = useState(null);
  useEffect(() => {
    let cancelled = false;
    apiGet('/health')
      .then((data) => {
        if (!cancelled) setApiHealth(data);
      })
      .catch(() => {
        if (!cancelled) setApiHealth({ status: 'error' });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const navigate = useCallback(
    (page) => {
      if (navigateTo) navigateTo(page);
    },
    [navigateTo],
  );

  const value = useMemo(
    () => ({
      wsStatus,
      setWsStatus,
      apiHealth,
      tenantId,
      setTenantId,
      executions,
      setExecutions,
      playgroundSource,
      setPlaygroundSource,
      navigateTo: navigate,
    }),
    [wsStatus, apiHealth, tenantId, executions, playgroundSource, navigate],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
