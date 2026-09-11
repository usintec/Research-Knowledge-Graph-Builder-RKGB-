import {
  InvalidEventEnvelopeError,
  createEventEnvelope,
  parseEventEnvelope,
  serializeEventEnvelope,
} from './index';

const input = {
  eventType: 'document.created',
  eventVersion: 1,
  producer: 'document-service',
  tenantId: 'tenant-1',
  actor: { id: 'user-1', type: 'user' as const },
  correlationId: 'corr-1',
  traceId: 'trace-1',
  aggregate: { type: 'document', id: 'doc-1' },
  data: { documentId: 'doc-1', objectKey: 'documents/doc-1.pdf' },
};

describe('versioned event envelope', () => {
  it('creates, serializes, and parses the complete contract', () => {
    const event = createEventEnvelope(input);
    const parsed = parseEventEnvelope(serializeEventEnvelope(event));
    expect(parsed).toMatchObject({
      eventType: 'document.created',
      tenantId: 'tenant-1',
      traceId: 'trace-1',
      aggregate: { type: 'document', id: 'doc-1' },
    });
  });

  it('rejects secrets and binary data in event payloads', () => {
    expect(() =>
      createEventEnvelope({ ...input, data: { password: 'not-allowed' } }),
    ).toThrow(InvalidEventEnvelopeError);
    expect(() =>
      createEventEnvelope({ ...input, data: { bytes: new Uint8Array([1, 2]) } }),
    ).toThrow(InvalidEventEnvelopeError);
  });

  it('rejects malformed JSON', () => {
    expect(() => parseEventEnvelope('{not-json')).toThrow(InvalidEventEnvelopeError);
  });
});