import { useEffect, useState } from 'react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';

function HealthRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-neutral-100 py-3 last:border-b-0">
      <span className="text-sm text-neutral-600">{label}</span>
      <span className="text-sm font-medium text-neutral-900">{value}</span>
    </div>
  );
}

function formatDate(value) {
  if (!value) {
    return '—';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatUptime(seconds) {
  if (seconds === null || seconds === undefined) {
    return '—';
  }

  const totalSeconds = Math.max(0, Math.floor(Number(seconds)));

  if (!Number.isFinite(totalSeconds)) {
    return '—';
  }

  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;

  const parts = [];

  if (days > 0) {
    parts.push(`${days}d`);
  }

  if (hours > 0 || days > 0) {
    parts.push(`${hours}h`);
  }

  if (minutes > 0 || hours > 0 || days > 0) {
    parts.push(`${minutes}m`);
  }

  parts.push(`${remainingSeconds}s`);

  return parts.join(' ');
}

function formatMemory(bytes) {
  if (bytes === null || bytes === undefined) {
    return '—';
  }

  const megabytes = Number(bytes) / (1024 * 1024);

  if (!Number.isFinite(megabytes)) {
    return '—';
  }

  return `${megabytes} MB`;
}

export default function Operations() {
  const [health, setHealth] = useState(null);
  const [violations, setViolations] = useState([]);

  const [loadingHealth, setLoadingHealth] = useState(true);
  const [loadingViolations, setLoadingViolations] = useState(true);

  const [healthError, setHealthError] = useState(null);
  const [violationsError, setViolationsError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const loadHealth = async () => {
      setLoadingHealth(true);
      setHealthError(null);

      try {
        const response = await fetch('/health');

        if (!response.ok) {
          throw new Error(
            `Health request failed (${response.status})`,
          );
        }

        const data = await response.json();

        if (!cancelled) {
          setHealth(data);
        }
      } catch (err) {
        if (!cancelled) {
          setHealthError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingHealth(false);
        }
      }
    };

    const loadViolations = async () => {
      setLoadingViolations(true);
      setViolationsError(null);

      try {
        const response = await fetch('/api/executions');

        if (!response.ok) {
          throw new Error(
            `Executions request failed (${response.status})`,
          );
        }

        const data = await response.json();

        if (!cancelled) {
          setViolations(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          setViolationsError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingViolations(false);
        }
      }
    };

    loadHealth();
    loadViolations();

    return () => {
      cancelled = true;
    };
  }, []);

  const status =
    health?.status === 'ok'
      ? 'Healthy'
      : health
        ? 'Unhealthy'
        : '—';

  return (
    <PageLayout>
      <PageBody>
        <div className="max-w-5xl space-y-5">
          <div>
            <h1 className="text-lg font-semibold text-neutral-900">
              Operations
            </h1>

            <p className="mt-1 text-sm text-neutral-500">
              Sandbox health and execution violations.
            </p>
          </div>

          <section className="rounded-xl border border-neutral-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-neutral-900">
              Sandbox health
            </h2>

            {healthError && (
              <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
                {healthError}
              </div>
            )}

            <div className="mt-3">
              <HealthRow
                label="Status"
                value={loadingHealth ? 'Loading…' : status}
              />

              <HealthRow
                label="Uptime"
                value={
                  loadingHealth
                    ? 'Loading…'
                    : formatUptime(health?.uptime_seconds)
                }
              />

              <HealthRow
                label="Fuel limit"
                value={
                  loadingHealth
                    ? 'Loading…'
                    : health?.fuel_limit
                      ? `${health.fuel_limit.toLocaleString()} fuel`
                      : '—'
                }
              />

              <HealthRow
                label="Memory cap"
                value={
                  loadingHealth
                    ? 'Loading…'
                    : formatMemory(health?.memory_cap_bytes)
                }
              />
            </div>
          </section>

          <section className="rounded-xl border border-neutral-200 bg-white p-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-neutral-900">
                  Violations
                </h2>

                <p className="mt-1 text-sm text-neutral-500">
                  Executions with a status other than OK.
                </p>
              </div>

              <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-700">
                {loadingViolations
                  ? 'Loading…'
                  : `${violations.length} records`}
              </span>
            </div>

            {violationsError && (
              <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
                {violationsError}
              </div>
            )}

            {loadingViolations ? (
              <div className="mt-6 text-sm text-neutral-500">
                Loading violations…
              </div>
            ) : violations.length === 0 ? (
              <div className="mt-6 rounded-lg border border-dashed border-neutral-200 p-6 text-center text-sm text-neutral-500">
                No violations recorded.
              </div>
            ) : (
              <div className="mt-4 overflow-x-auto">
                <table className="w-full min-w-[700px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-neutral-200 text-xs uppercase tracking-wide text-neutral-500">
                      <th className="px-3 py-3 font-medium">Time</th>
                      <th className="px-3 py-3 font-medium">Status</th>
                      <th className="px-3 py-3 font-medium">Duration</th>
                      <th className="px-3 py-3 font-medium">Artifact</th>
                      <th className="px-3 py-3 font-medium">Error</th>
                    </tr>
                  </thead>

                  <tbody>
                    {violations.map((execution) => (
                      <tr
                        key={execution.id}
                        className="border-b border-neutral-100 last:border-b-0"
                      >
                        <td className="px-3 py-3 text-neutral-600">
                          {formatDate(execution.created_at)}
                        </td>

                        <td className="px-3 py-3">
                          <span className="rounded-full bg-rose-100 px-2 py-1 text-xs font-medium text-rose-700">
                            {execution.status}
                          </span>
                        </td>

                        <td className="px-3 py-3 text-neutral-600">
                          {execution.duration_ms} ms
                        </td>

                        <td className="px-3 py-3 font-mono text-xs text-neutral-600">
                          {execution.artifact_id || '—'}
                        </td>

                        <td className="max-w-md px-3 py-3 text-neutral-600">
                          {execution.stderr || '—'}
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