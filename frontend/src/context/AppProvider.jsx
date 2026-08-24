import { useCallback, useEffect, useMemo, useState } from 'react';
import { AppContext } from './AppContext';
import { apiGet } from '../lib/api';

export function AppProvider({ navigateTo, children }) {
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [apiHealth, setApiHealth] = useState(null);
  const [tenantId, setTenantId] = useState('tenant_a');
  const [executions, setExecutions] = useState([]);

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
      navigateTo: navigate,
    }),
    [wsStatus, apiHealth, tenantId, executions, navigate],
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
