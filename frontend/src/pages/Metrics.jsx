import { useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { GRAFANA_DASHBOARD_URL, PROMETHEUS_URL } from '../lib/observability';

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
  const [stats] = useState({ timeouts: 0, oom: 0, compileErrors: 0 });

  return (
    <PageLayout>
      <PageBody>
        <div className="space-y-4 max-w-5xl">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard label="Sandbox timeouts" value={stats.timeouts} hint="wasmbox_sandbox_timeouts_total" />
            <StatCard label="Out-of-memory kills" value={stats.oom} hint="wasmbox_oom_total" />
            <StatCard label="Compile errors" value={stats.compileErrors} hint="wasmbox_compile_errors_total" />
          </div>

          <div className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">Observability</h2>
            <p className="text-sm text-neutral-500 mt-1">
              Stat cards above will pull live from <code>/metrics</code>. Use Grafana/Prometheus below for deeper dives.
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