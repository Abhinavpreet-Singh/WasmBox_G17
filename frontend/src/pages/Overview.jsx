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
              <div className="overflow-x-auto rounded-lg border border-neutral-200">
                <table className="min-w-full text-left text-sm">
                  <thead className="bg-neutral-50 text-xs uppercase text-neutral-500">
                    <tr>
                      <th className="px-3 py-2 font-semibold">Status</th>
                      <th className="px-3 py-2 font-semibold">Artifact</th>
                      <th className="px-3 py-2 font-semibold">Duration</th>
                      <th className="px-3 py-2 font-semibold">Output</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-200">
                    {executions.map((ex, i) => (
                      <tr key={i} className="text-neutral-700">
                        <td className="px-3 py-2">
                          <span
                            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${ex.status === 'ok'
                                ? 'bg-emerald-100 text-emerald-700'
                                : ex.status === 'timeout'
                                  ? 'bg-amber-100 text-amber-700'
                                  : 'bg-neutral-100 text-neutral-700'
                              }`}
                          >
                            {ex.status || 'unknown'}
                          </span>
                        </td>
                        <td className="px-3 py-2 font-mono">
                          {ex.artifact || ex.artifact_id || '—'}
                        </td>
                        <td className="px-3 py-2 font-mono">
                          {ex.duration_ms ?? '—'} ms
                        </td>
                        <td className="max-w-md truncate px-3 py-2 font-mono">
                          {ex.stdout || ex.message || ex.stderr || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </PageBody>
    </PageLayout>
  );
}
