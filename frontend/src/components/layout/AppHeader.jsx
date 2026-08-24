import { useApp } from '../../hooks/useApp';
import { NAV_ITEMS } from '../../config/navigation';
import { GRAFANA_URL, PROMETHEUS_URL } from '../../lib/observability';

export default function AppHeader({ activePage }) {
  const { wsStatus, apiHealth, tenantId, setTenantId } = useApp();
  const page = NAV_ITEMS.find((item) => item.id === activePage);
  const apiOk = apiHealth?.status === 'ok';

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-white border-b border-neutral-200 shrink-0 min-h-[3.25rem]">
      <div className="min-w-0">
        <h1 className="text-sm font-semibold text-neutral-900 truncate">{page?.label ?? 'Dashboard'}</h1>
        <p className="text-[10px] text-neutral-400 font-mono truncate hidden sm:block">
          {page?.description}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs font-mono">
        <label className="flex items-center gap-1.5 text-neutral-500">
          Tenant
          <select
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="text-neutral-900 bg-neutral-50 border border-neutral-200 rounded px-1.5 py-0.5 text-xs"
          >
            <option value="tenant_a">tenant_a</option>
            <option value="tenant_b">tenant_b</option>
          </select>
        </label>
        <span className={`flex items-center gap-1 ${apiOk ? 'text-emerald-600' : 'text-amber-600'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${apiOk ? 'bg-emerald-500' : 'bg-amber-500'}`} />
          API
        </span>
        <span
          className={`flex items-center gap-1.5 font-bold ${wsStatus === 'connected' ? 'text-emerald-600' : 'text-neutral-400'}`}
        >
          <span
            className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500' : 'bg-neutral-300'}`}
          />
          <span className="hidden sm:inline">WS</span>
        </span>
        <a
          href={GRAFANA_URL}
          target="_blank"
          rel="noreferrer"
          className="px-2 py-1 rounded border border-neutral-200 bg-neutral-50 hover:bg-neutral-100 text-neutral-600"
        >
          Grafana
        </a>
        <a
          href={PROMETHEUS_URL}
          target="_blank"
          rel="noreferrer"
          className="px-2 py-1 rounded border border-neutral-200 bg-neutral-50 hover:bg-neutral-100 text-neutral-600 hidden sm:inline"
        >
          Prometheus
        </a>
      </div>
    </header>
  );
}
