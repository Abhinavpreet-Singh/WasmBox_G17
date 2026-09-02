import { useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { apiPost } from '../lib/api';

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

export default function SecurityLab() {
  const [results, setResults] = useState({});
  const [loadingId, setLoadingId] = useState(null);

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
    } catch (error) {
      setResults((previous) => ({
        ...previous,
        [scenario.id]: {
          status: 'error',
          message: error.message,
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

    return 'bg-neutral-100 text-neutral-700';
  };

  return (
    <PageLayout>
      <PageBody>
        <div className="mx-auto max-w-6xl space-y-6">
          <header>
            <h2 className="text-lg font-semibold text-neutral-900">
              Security Lab
            </h2>
            <p className="mt-1 text-sm text-neutral-500">
              Fire curated attacks and watch the sandbox reject them in real time.
            </p>
          </header>

          <div className="grid gap-4 md:grid-cols-2">
            {ATTACK_SCENARIOS.map((scenario) => {
              const result = results[scenario.id];

              return (
                <article
                  key={scenario.id}
                  className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm"
                >
                  <h3 className="font-semibold text-neutral-900">
                    {scenario.title}
                  </h3>
                  <p className="mt-1 text-sm text-neutral-500">
                    {scenario.description}
                  </p>

                  <pre className="mt-4 overflow-x-auto rounded-lg bg-neutral-950 p-3 text-xs text-neutral-100">
                    <code>{scenario.source}</code>
                  </pre>

                  <button
                    type="button"
                    onClick={() => handleFireAttack(scenario)}
                    disabled={loadingId !== null}
                    className="mt-4 rounded-lg bg-rose-600 px-3 py-2 text-xs font-semibold text-white hover:bg-rose-500 disabled:opacity-50"
                  >
                    {loadingId === scenario.id ? 'Firing...' : 'Fire Attack'}
                  </button>

                  {result && (
                    <div className="mt-4 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
                      <span
                        className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${badgeClass(result.status)}`}
                      >
                        {result.status}
                      </span>
                      <p className="mt-2 text-sm text-neutral-700">
                        {result.stderr || result.message || 'No reason returned.'}
                      </p>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}