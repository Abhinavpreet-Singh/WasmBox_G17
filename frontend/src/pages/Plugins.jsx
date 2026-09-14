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
        <div className="mx-auto max-w-6xl space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-neutral-900">
                Plugin Registry
              </h2>
              <p className="mt-1 text-sm text-neutral-500">
                Browse saved plugins and their latest versions.
              </p>
            </div>

            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search plugins..."
              className="w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 sm:w-64"
            />
          </div>

          {loading && (
            <p className="text-sm text-neutral-500">Loading plugins...</p>
          )}

          {error && (
            <p className="rounded-lg bg-rose-50 p-3 text-sm text-rose-700">
              {error}
            </p>
          )}

          {!loading && !error && filteredPlugins.length === 0 && (
            <div className="rounded-xl border border-dashed border-neutral-300 bg-white p-8 text-center">
              <p className="text-sm text-neutral-500">
                No matching plugins found.
              </p>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {filteredPlugins.map((plugin) => (
              <article
                key={plugin.id}
                className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-semibold text-neutral-900">
                    {plugin.name}
                  </h3>
                  <span className="rounded-full bg-indigo-50 px-2 py-1 text-xs font-semibold text-indigo-700">
                    v{plugin.latest_version}
                  </span>
                </div>

                <pre className="mt-4 max-h-32 overflow-auto whitespace-pre-wrap rounded-lg bg-neutral-950 p-3 text-xs text-neutral-200">
                  {plugin.source}
                </pre>

                <div className="mt-4 space-y-1 text-xs text-neutral-500">
                  <p className="font-mono">
                    SHA: {plugin.sha256.slice(0, 12)}...
                  </p>
                  <p>
                    Saved: {new Date(plugin.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => handleLoad(plugin)}
                    className="rounded-lg border border-indigo-200 px-3 py-2 text-xs font-semibold text-indigo-700 hover:bg-indigo-50"
                  >
                    Load in Playground
                  </button>

                  <button
                    type="button"
                    onClick={() => handleRun(plugin)}
                    disabled={runningId === plugin.id}
                    className="rounded-lg bg-neutral-900 px-3 py-2 text-xs font-semibold text-white hover:bg-neutral-700 disabled:opacity-50"
                  >
                    {runningId === plugin.id ? 'Running...' : 'Run'}
                  </button>
                </div>

                {actionError?.pluginId === plugin.id && (
                  <p className="mt-3 rounded-lg bg-rose-50 p-2 text-xs text-rose-700">
                    {actionError.message}
                  </p>
                )}

                {runResults[plugin.id] && (
                  <div className="mt-3 rounded-lg bg-neutral-100 p-3 text-xs">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 font-semibold ${runResults[plugin.id].status === 'ok'
                          ? 'bg-emerald-100 text-emerald-700'
                          : runResults[plugin.id].status === 'timeout'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-rose-100 text-rose-700'
                        }`}
                    >
                      {runResults[plugin.id].status}
                    </span>

                    <p className="mt-2 whitespace-pre-wrap text-neutral-700">
                      {runResults[plugin.id].stdout ||
                        runResults[plugin.id].stderr ||
                        runResults[plugin.id].message ||
                        'No output returned.'}
                    </p>
                  </div>
                )}
              </article>
            ))}
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}