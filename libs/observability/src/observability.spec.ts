import {
  CorrelationContextStore,
  createTraceMetadata,
  traceMetadataFromHeaders,
  traceMetadataToHeaders,
} from './index';

describe('observability primitives', () => {
  it('round-trips correlation and trace metadata through headers', () => {
    const metadata = createTraceMetadata('corr-1', 'trace-1', {
      tenantId: 'tenant-1',
      actorId: 'actor-1',
    });
    const headers = traceMetadataToHeaders(metadata);
    expect(traceMetadataFromHeaders(headers)).toMatchObject(metadata);
  });

  it('propagates context across async work', async () => {
    const store = new CorrelationContextStore();
    const metadata = createTraceMetadata('corr-async', 'trace-async');
    await store.runAsync(metadata, async () => {
      await Promise.resolve();
      expect(store.get()).toEqual(metadata);
    });
    expect(store.get()).toBeUndefined();
  });
});