import PageLayout, { PageBody } from '../components/layout/PageLayout';

export default function SecurityLab() {
  return (
    <PageLayout>
      <PageBody>
        <div className="rounded-xl border border-dashed border-neutral-300 bg-white p-8 text-center max-w-lg mx-auto">
          <h2 className="text-sm font-semibold text-neutral-900">Security Lab</h2>
          <p className="text-sm text-neutral-500 mt-2">
            Curated attack cards with denial reasons — Week 3 Days 11–12.
          </p>
        </div>
      </PageBody>
    </PageLayout>
  );
}
