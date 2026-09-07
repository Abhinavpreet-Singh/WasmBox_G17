import { useEffect, useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { GRAFANA_DASHBOARD_URL, PROMETHEUS_URL } from '../lib/observability';
import { apiGetText } from '../lib/api';
import { parsePrometheusText, pickStat } from '../lib/metrics';

const POLL_INTERVAL_MS = 5000;

function StatCard({ label, value, hint }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5">
      <p className="text-xs font-medium text-neutral-500">{label}</p>
      <p className="text-2xl font-semibold text-neutral-900 mt-1">{value}</p>
      {hint && <p className="text-xs text-neutral-400 mt-1 font-mono">{hint}</p>}
    </div>
  );
}

function StatCard({ label, value, hint }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5">
      <p className="text-xs font-medium text-neutral-500">{label}</p>
      <p className="text-2xl font-semibold text-neutral-900 mt-1">{value}</p>
      {hint && <p className="text-xs text-neutral-400 mt-1 font-mono">{hint}</p>}
    </div>
  );
}

export default function Metrics() {
  const [stats, setStats] = useState({ timeouts: 0, oom: 0, compileErrors: 0 });
  const [status, setStatus] = useState('loading'); // loading | ok | error
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function fetchMetrics() {
      try {
        const text = await apiGetText('/metrics');
        if (cancelled) return;
        const values = parsePrometheusText(text);
        setStats({
          timeouts: pickStat(values, 'wasmbox_sandbox_timeouts_total'),
          oom: pickStat(values, 'wasmbox_oom_total'),
          compileErrors: pickStat(values, 'wasmbox_compile_errors_total'),
        });
        setStatus('ok');
      } catch (err) {
        if (cancelled) return;
        setError(err.message);
        setStatus('error');
      }
    }

    fetchMetrics();
    const id = setInterval(fetchMetrics, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <PageLayout>
      <PageBody>
        <div className="space-y-4 max-w-5xl">
          {status === 'error' && (
            <div className="rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm px-3 py-2">
              Couldn't reach /metrics: {error}
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard label="Sandbox timeouts" value={status === 'loading' ? '—' : stats.timeouts} hint="wasmbox_sandbox_timeouts_total" />
            <StatCard label="Out-of-memory kills" value={status === 'loading' ? '—' : stats.oom} hint="wasmbox_oom_total" />
            <StatCard label="Compile errors" value={status === 'loading' ? '—' : stats.compileErrors} hint="wasmbox_compile_errors_total" />
          </div>

          <div className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">Observability</h2>
            <p className="text-sm text-neutral-500 mt-1">
              Stat cards above poll <code>/metrics</code> every {POLL_INTERVAL_MS / 1000}s. Use Grafana/Prometheus below for deeper dives.
            </p>
            <div className="flex gap-2 mt-4 text-xs font-mono">
              <a href={GRAFANA_DASHBOARD_URL} target="_blank" rel="noreferrer" className="px-2 py-1 rounded border border-neutral-200 hover:bg-neutral-50">
                Open Grafana dashboard
              </a>
              <a href={PROMETHEUS_URL} target="_blank" rel="noreferrer" className="px-2 py-1 rounded border border-neutral-200 hover:bg-neutral-50">
                Open Prometheus
              </a>
            </div>
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}