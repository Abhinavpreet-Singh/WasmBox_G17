import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { useApp } from '../hooks/useApp';

export default function Overview() {
  const { apiHealth, executions, navigateTo } = useApp();

  return (
    <PageLayout>
      <PageBody>
        <div className="max-w-5xl space-y-6">
          <section className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">Sandbox status</h2>
            <p className="text-sm text-neutral-500 mt-1">
              API: <span className="font-mono text-neutral-800">{apiHealth?.status ?? 'checking…'}</span>
              {apiHealth?.service && (
                <span className="text-neutral-400"> · {apiHealth.service}</span>
              )}
            </p>
            <p className="text-xs text-neutral-400 mt-3">
              Week 1 scaffold — executions table fills in Week 2 Day 10.
            </p>
          </section>

          <section className="rounded-xl border border-neutral-200 bg-white p-5">
            <div className="flex items-center justify-between gap-3 mb-4">
              <h2 className="text-sm font-semibold text-neutral-900">Recent executions</h2>
              <button
                type="button"
                onClick={() => navigateTo('playground')}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800"
              >
                Open Playground →
              </button>
            </div>
            {executions.length === 0 ? (
              <p className="text-sm text-neutral-400">No executions yet. Compile and run a plugin.</p>
            ) : (
              <ul className="text-sm font-mono text-neutral-600 space-y-1">
                {executions.map((ex, i) => (
                  <li key={i}>{JSON.stringify(ex)}</li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </PageBody>
    </PageLayout>
  );
}
