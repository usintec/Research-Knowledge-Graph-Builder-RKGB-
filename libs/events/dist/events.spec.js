"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("./index");
const input = {
    eventType: 'document.created',
    eventVersion: 1,
    producer: 'document-service',
    tenantId: 'tenant-1',
    actor: { id: 'user-1', type: 'user' },
    correlationId: 'corr-1',
    traceId: 'trace-1',
    aggregate: { type: 'document', id: 'doc-1' },
    data: { documentId: 'doc-1', objectKey: 'documents/doc-1.pdf' },
};
describe('versioned event envelope', () => {
    it('creates, serializes, and parses the complete contract', () => {
        const event = (0, index_1.createEventEnvelope)(input);
        const parsed = (0, index_1.parseEventEnvelope)((0, index_1.serializeEventEnvelope)(event));
        expect(parsed).toMatchObject({
            eventType: 'document.created',
            tenantId: 'tenant-1',
            traceId: 'trace-1',
            aggregate: { type: 'document', id: 'doc-1' },
        });
    });
    it('rejects secrets and binary data in event payloads', () => {
        expect(() => (0, index_1.createEventEnvelope)({ ...input, data: { password: 'not-allowed' } })).toThrow(index_1.InvalidEventEnvelopeError);
        expect(() => (0, index_1.createEventEnvelope)({ ...input, data: { bytes: new Uint8Array([1, 2]) } })).toThrow(index_1.InvalidEventEnvelopeError);
    });
    it('rejects malformed JSON', () => {
        expect(() => (0, index_1.parseEventEnvelope)('{not-json')).toThrow(index_1.InvalidEventEnvelopeError);
    });
});
//# sourceMappingURL=events.spec.js.map