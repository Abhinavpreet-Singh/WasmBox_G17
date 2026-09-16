import { useEffect, useMemo, useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { apiGet, apiPost } from '../lib/api';
import { useApp } from '../hooks/useApp';
export default function Plugins() {
  const {
    navigateTo,
    setPlaygroundSource,
    setExecutions,
  } = useApp();
  const [plugins, setPlugins] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [runningId, setRunningId] = useState(null);
  const [runResults, setRunResults] = useState({});
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    apiGet('/api/plugins')
      .then((data) => {
        if (!cancelled) setPlugins(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredPlugins = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) return plugins;

    return plugins.filter((plugin) =>
      plugin.name.toLowerCase().includes(query),
    );
  }, [plugins, search]);
  const handleLoad = (plugin) => {
    setPlaygroundSource(plugin.source);
    navigateTo('playground');
  };

  const handleRun = async (plugin) => {
    setRunningId(plugin.id);
    setActionError(null);

    try {
      const data = await apiPost(`/api/plugins/${plugin.id}/run`, {});
      setRunResults((previous) => ({
        ...previous,
        [plugin.id]: data,
      }));
      setExecutions((previous) => [data, ...previous].slice(0, 20));
    } catch (err) {
      setActionError({
        pluginId: plugin.id,
        message: err.message,
      });
    } finally {
      setRunningId(null);
    }
  };
  return (
    <PageLayout>
      <PageBody>
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Left panel */}
          <section className="rounded-xl border border-neutral-200 bg-white p-6">
            <h2 className="text-lg font-semibold text-neutral-900">
              Create Plugin
            </h2>
            <p className="mt-1 text-sm text-neutral-500">
              Compile and save a Python WASM plugin.
            </p>
          </section>

          {/* Right panel */}
          <section className="rounded-xl border border-neutral-200 bg-white p-6">
            <h2 className="text-lg font-semibold text-neutral-900">
              Saved Plugins
            </h2>
            <p className="mt-1 text-sm text-neutral-500">
              Your compiled plugins will appear here.
            </p>
          </section>
        </div>
      </PageBody>
    </PageLayout>
  );
}