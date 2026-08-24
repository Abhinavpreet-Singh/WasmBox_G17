import PageLayout, { PageBody } from '../components/layout/PageLayout';

export default function Plugins() {
  return (
    <PageLayout>
      <PageBody>
        <div className="rounded-xl border border-dashed border-neutral-300 bg-white p-8 text-center max-w-lg mx-auto">
          <h2 className="text-sm font-semibold text-neutral-900">Plugins</h2>
          <p className="text-sm text-neutral-500 mt-2">
            Save, version, and webhook configuration — Week 3 Day 14–18.
          </p>
        </div>
      </PageBody>
    </PageLayout>
  );
}
