import { useState } from 'react';
import Editor from '@monaco-editor/react';
import PageLayout, { PageBody } from '../components/layout/PageLayout';
import { apiPost } from '../lib/api';
import { useApp } from '../hooks/useApp';

const DEFAULT_SOURCE = `# WasmBox plugin (Extism PDK — Week 2)
from extism import plugin_fn

@plugin_fn
def greet():
    return "Hello from WasmBox!"
`;

export default function Playground() {
  const { setExecutions } = useApp();
  const [source, setSource] = useState(DEFAULT_SOURCE);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost('/api/run', { source });
      setResult(data);
      setExecutions((prev) => [data, ...prev].slice(0, 20));
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };
  const handleRunHello = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiPost('/api/run/wasm', {
        artifact: 'hello.wasm',
        stdin: '',
      });

      setResult(data);
      setExecutions((prev) => [data, ...prev].slice(0, 20));
    } catch (e) {
      setError(e.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };
  return (
    <PageLayout>
      <PageBody className="!p-0 flex flex-col">
        <div className="flex items-center gap-2 px-4 py-2 border-b border-neutral-200 bg-white shrink-0">
          <button
            type="button"
            onClick={handleRun}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-neutral-900 text-white hover:bg-neutral-800 disabled:opacity-50"
          >
            {loading ? 'Running…' : 'Run (stub)'}
          </button>
          <button
            type="button"
            onClick={handleRunHello}
            disabled={loading}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run hello.wasm'}
          </button>
          <span className="text-[10px] text-neutral-400 font-mono">Compile → Week 2 Day 7</span>
        </div>
        <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-neutral-200">
          <div className="min-h-[280px] lg:min-h-0">
            <Editor
              height="100%"
              defaultLanguage="python"
              value={source}
              onChange={(v) => setSource(v ?? '')}
              theme="vs-light"
              options={{
                fontSize: 13,
                minimap: { enabled: false },
                padding: { top: 12 },
              }}
            />
          </div>
          <div className="p-4 font-mono text-xs overflow-auto bg-neutral-900 text-neutral-100 min-h-[200px]">
            {error && <p className="text-rose-400 mb-2">{error}</p>}
            {result ? (
              <div className="space-y-4">
                <div>
                  <p className="mb-1 text-neutral-400">stdout</p>
                  <pre className="whitespace-pre-wrap">
                    {result.stdout || '(no stdout)'}
                  </pre>
                </div>
                <p className="text-neutral-400">
                  Duration: {result.duration_ms} ms
                </p>
              </div>
            ) : (
              <p className="text-neutral-500">Output appears here after Run.</p>
            )}
          </div>
        </div>
      </PageBody>
    </PageLayout>
  );
}
