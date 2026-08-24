import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { GRAFANA_DASHBOARD_URL, PROMETHEUS_URL } from '../lib/observability';

export default function Metrics() {
  return (
    <PageLayout>
      <PageBody>
        <div className="space-y-4 max-w-5xl">
          <div className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">Observability</h2>
            <p className="text-sm text-neutral-500 mt-1">
              Grafana embeds and stat cards — Week 4 Day 19.
            </p>
            <div className="flex gap-2 mt-4 text-xs font-mono">
              <a
                href={GRAFANA_DASHBOARD_URL}
                target="_blank"
                rel="noreferrer"
                className="px-2 py-1 rounded border border-neutral-200 hover:bg-neutral-50"
              >
                Open Grafana dashboard
              </a>
              <a
                href={PROMETHEUS_URL}
                target="_blank"
                rel="noreferrer"
                className="px-2 py-1 rounded border border-neutral-200 hover:bg-neutral-50"
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
