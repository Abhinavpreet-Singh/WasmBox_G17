import { useEffect, useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import {
  GRAFANA_DASHBOARD_URL,
  PROMETHEUS_URL,
} from '../lib/observability';

const METRICS = {
  sandboxTimeouts: 'wasmbox_sandbox_timeouts_total',
  oom: 'wasmbox_oom_total',
  compileErrors: 'wasmbox_compile_errors_total',
  executions: 'wasmbox_executions_total',
};

function parsePrometheusMetric(text, metricName) {
  const escapedName = metricName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const pattern = new RegExp(
    `^${escapedName}(?:\\{[^}]*\\})?\\s+([-+]?\\d+(?:\\.\\d+)?(?:[eE][-+]?\\d+)?)$`,
    'm',
  );

  const match = text.match(pattern);

  if (!match) {
    return 0;
  }

  const value = Number(match[1]);

  return Number.isFinite(value) ? value : 0;
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold text-neutral-900">
        {value}
      </p>
    </div>
  );
}

export default function Metrics() {
  const [metrics, setMetrics] = useState({
    sandboxTimeouts: 0,
    oom: 0,
    compileErrors: 0,
    executions: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const loadMetrics = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('/metrics');

        if (!response.ok) {
          throw new Error(
            `Metrics request failed (${response.status})`,
          );
        }

        const text = await response.text();

        if (cancelled) {
          return;
        }

        setMetrics({
          sandboxTimeouts: parsePrometheusMetric(
            text,
            METRICS.sandboxTimeouts,
          ),

          oom: parsePrometheusMetric(
            text,
            METRICS.oom,
          ),

          compileErrors: parsePrometheusMetric(
            text,
            METRICS.compileErrors,
          ),

          executions: parsePrometheusMetric(
            text,
            METRICS.executions,
          ),
        });
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadMetrics();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <PageLayout>
      <PageBody>
        <div className="space-y-5 max-w-5xl">
          <div>
            <h1 className="text-lg font-semibold text-neutral-900">
              Metrics
            </h1>

            <p className="mt-1 text-sm text-neutral-500">
              Sandbox execution and failure metrics from Prometheus.
            </p>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Sandbox timeouts"
              value={loading ? '—' : metrics.sandboxTimeouts}
            />

            <StatCard
              label="OOM events"
              value={loading ? '—' : metrics.oom}
            />

            <StatCard
              label="Compile errors"
              value={loading ? '—' : metrics.compileErrors}
            />

            <StatCard
              label="Total executions"
              value={loading ? '—' : metrics.executions}
            />
          </div>

          <div className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">
              Observability
            </h2>

            <p className="mt-1 text-sm text-neutral-500">
              Open the external observability tools for detailed
              metrics and dashboards.
            </p>

            <div className="mt-4 flex flex-wrap gap-2 text-xs font-mono">
              <a
                href={GRAFANA_DASHBOARD_URL}
                target="_blank"
                rel="noreferrer"
                className="rounded border border-neutral-200 px-2 py-1 hover:bg-neutral-50"
              >
                Open Grafana dashboard
              </a>

              <a
                href={PROMETHEUS_URL}
                target="_blank"
                rel="noreferrer"
                className="rounded border border-neutral-200 px-2 py-1 hover:bg-neutral-50"
              >
                Open Prometheus
              </a>
            </div>
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}