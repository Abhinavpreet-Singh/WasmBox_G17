import { useCallback, useEffect, useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { apiGet, apiPost } from '../lib/api';

const ATTACK_SCENARIOS = [
  {
    id: 'file-read',
    title: 'File Read',
    description: 'Attempts to read a protected operating-system file.',
    source: 'open("/etc/passwd").read()',
  },
  {
    id: 'infinite-loop',
    title: 'Infinite Loop',
    description: 'Attempts to consume execution time without terminating.',
    source: 'while True:\n    pass',
  },
  {
    id: 'subprocess-spawn',
    title: 'Subprocess Spawn',
    description: 'Attempts to launch an operating-system subprocess.',
    source: 'import subprocess\nsubprocess.run(["whoami"])',
  },
  {
    id: 'eval-injection',
    title: 'Eval Injection',
    description: 'Attempts to execute dynamically injected Python code.',
    source: 'eval(\'__import__("os").system("whoami")\')',
  },
];

const formatAttackType = (attackType) => {
  if (!attackType) {
    return 'Unknown';
  }

  return attackType
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
};

export default function SecurityLab() {
  const [stats, setStats] = useState(null);
  const [feed, setFeed] = useState([]);
  const [results, setResults] = useState({});
  const [loadingId, setLoadingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadSecurityData = useCallback(async () => {
    try {
      setError(null);

      const [statsData, feedData] = await Promise.all([
        apiGet('/api/security/stats'),
        apiGet('/api/security/feed'),
      ]);

      setStats(statsData);
      setFeed(feedData);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSecurityData();
  }, [loadSecurityData]);

  const handleFireAttack = async (scenario) => {
    setLoadingId(scenario.id);

    try {
      const data = await apiPost('/api/run', {
        source: scenario.source,
      });

      setResults((previous) => ({
        ...previous,
        [scenario.id]: data,
      }));

      await loadSecurityData();
    } catch (requestError) {
      setResults((previous) => ({
        ...previous,
        [scenario.id]: {
          status: 'error',
          message: requestError.message,
        },
      }));
    } finally {
      setLoadingId(null);
    }
  };

  const badgeClass = (status) => {
    if (status === 'blocked') {
      return 'bg-rose-100 text-rose-700';
    }

    if (status === 'timeout') {
      return 'bg-amber-100 text-amber-700';
    }

    if (status === 'completed') {
      return 'bg-emerald-100 text-emerald-700';
    }

    return 'bg-neutral-100 text-neutral-700';
  };

  return (
    <PageLayout>
      <PageBody>
        <div className="mx-auto max-w-7xl space-y-6">
          <header>
            <h2 className="text-lg font-semibold text-neutral-900">
              Security Lab
            </h2>

            <p className="mt-1 text-sm text-neutral-500">
              Monitor sandbox security activity and fire curated attacks.
            </p>
          </header>

          {error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
              Unable to load security data: {error}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            {/* LEFT COLUMN */}
            <section className="space-y-6">
              {/* Security Overview */}
              <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-neutral-900">
                  Security Overview
                </h3>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="rounded-lg bg-neutral-50 p-4">
                    <p className="text-xs font-medium text-neutral-500">
                      Total Executions
                    </p>

                    <p className="mt-1 text-2xl font-semibold text-neutral-900">
                      {loading ? '—' : stats?.total_executions ?? 0}
                    </p>
                  </div>

                  <div className="rounded-lg bg-emerald-50 p-4">
                    <p className="text-xs font-medium text-emerald-700">
                      Safe Executions
                    </p>

                    <p className="mt-1 text-2xl font-semibold text-emerald-900">
                      {loading ? '—' : stats?.safe_executions ?? 0}
                    </p>
                  </div>

                  <div className="rounded-lg bg-rose-50 p-4">
                    <p className="text-xs font-medium text-rose-700">
                      Detected Attacks
                    </p>

                    <p className="mt-1 text-2xl font-semibold text-rose-900">
                      {loading ? '—' : stats?.detected_attacks ?? 0}
                    </p>
                  </div>

                  <div className="rounded-lg bg-blue-50 p-4">
                    <p className="text-xs font-medium text-blue-700">
                      Avg Duration
                    </p>

                    <p className="mt-1 text-2xl font-semibold text-blue-900">
                      {loading
                        ? '—'
                        : `${stats?.average_duration_ms ?? 0} ms`}
                    </p>
                  </div>
                </div>
              </div>

              {/* Attack Breakdown */}
              <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-neutral-900">
                  Attack Breakdown
                </h3>

                {stats?.attack_counts &&
                Object.keys(stats.attack_counts).length > 0 ? (
                  <div className="mt-4 space-y-3">
                    {Object.entries(stats.attack_counts).map(
                      ([attackType, count]) => (
                        <div
                          key={attackType}
                          className="flex items-center justify-between rounded-lg bg-neutral-50 px-3 py-2"
                        >
                          <span className="text-sm text-neutral-700">
                            {formatAttackType(attackType)}
                          </span>

                          <span className="rounded-full bg-rose-100 px-2 py-0.5 text-xs font-semibold text-rose-700">
                            {count}
                          </span>
                        </div>
                      ),
                    )}
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-neutral-500">
                    No attacks detected yet.
                  </p>
                )}
              </div>

              {/* Security Feed */}
              <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
                <h3 className="font-semibold text-neutral-900">
                  Security Feed
                </h3>

                {feed.length === 0 ? (
                  <p className="mt-4 text-sm text-neutral-500">
                    No security events recorded yet.
                  </p>
                ) : (
                  <div className="mt-4 max-h-80 space-y-2 overflow-y-auto">
                    {feed.map((execution) => (
                      <div
                        key={execution.id}
                        className="rounded-lg border border-neutral-100 bg-neutral-50 p-3"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-sm font-medium text-neutral-900">
                            {formatAttackType(execution.attack_type)}
                          </span>

                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-semibold ${badgeClass(
                              execution.status,
                            )}`}
                          >
                            {execution.status}
                          </span>
                        </div>

                        <p className="mt-1 text-xs text-neutral-500">
                          {execution.duration_ms} ms
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            {/* RIGHT COLUMN */}
            <section className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
              <h3 className="font-semibold text-neutral-900">
                Attack Scenarios
              </h3>

              <p className="mt-1 text-sm text-neutral-500">
                Fire curated attacks and watch the sandbox reject them.
              </p>

              <div className="mt-4 space-y-4">
                {ATTACK_SCENARIOS.map((scenario) => {
                  const result = results[scenario.id];

                  return (
                    <article
                      key={scenario.id}
                      className="rounded-xl border border-neutral-200 p-4"
                    >
                      <h4 className="font-semibold text-neutral-900">
                        {scenario.title}
                      </h4>

                      <p className="mt-1 text-sm text-neutral-500">
                        {scenario.description}
                      </p>

                      <pre className="mt-3 overflow-x-auto rounded-lg bg-neutral-950 p-3 text-xs text-neutral-100">
                        <code>{scenario.source}</code>
                      </pre>

                      <button
                        type="button"
                        onClick={() => handleFireAttack(scenario)}
                        disabled={loadingId !== null}
                        className="mt-3 rounded-lg bg-rose-600 px-3 py-2 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
                      >
                        {loadingId === scenario.id
                          ? 'Firing...'
                          : 'Fire Attack'}
                      </button>

                      {result && (
                        <div className="mt-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
                          <span
                            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${badgeClass(
                              result.status,
                            )}`}
                          >
                            {result.status}
                          </span>

                          <p className="mt-2 text-sm text-neutral-700">
                            {result.stderr ||
                              result.message ||
                              'No reason returned.'}
                          </p>
                        </div>
                      )}
                    </article>
                  );
                })}
              </div>
            </section>
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}