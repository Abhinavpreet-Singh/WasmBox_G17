import PageLayout, { PageBody } from '../components/layout/PageLayout';

export default function Plugins() {
  return (
    <PageLayout>
      <PageBody>
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Left panel */}
          <section className="rounded-xl border border-neutral-200 bg-white p-6">
            <h2 className="text-lg font-semibold text-neutral-900">
              Create Plugin
            </h2>
            <p className="mt-1 text-sm text-neutral-500">
              Compile and save a Python WASM plugin.
            </p>
          </section>

          {/* Right panel */}
          <section className="rounded-xl border border-neutral-200 bg-white p-6">
            <h2 className="text-lg font-semibold text-neutral-900">
              Saved Plugins
            </h2>
            <p className="mt-1 text-sm text-neutral-500">
              Your compiled plugins will appear here.
            </p>
          </section>
        </div>
      </PageBody>
    </PageLayout>
  );
}
