"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InvalidEventEnvelopeError = void 0;
exports.assertSafeEventData = assertSafeEventData;
exports.validateEventEnvelope = validateEventEnvelope;
exports.createEventEnvelope = createEventEnvelope;
exports.serializeEventEnvelope = serializeEventEnvelope;
exports.parseEventEnvelope = parseEventEnvelope;
const node_crypto_1 = require("node:crypto");
const FORBIDDEN_KEYS = new Set([
    'access_token',
    'authorization',
    'client_secret',
    'password',
    'private_key',
    'refresh_token',
    'secret',
    'token',
]);
const MAX_EVENT_BYTES = 1024 * 1024;
class InvalidEventEnvelopeError extends Error {
    constructor(message) {
        super(message);
        this.name = 'InvalidEventEnvelopeError';
    }
}
exports.InvalidEventEnvelopeError = InvalidEventEnvelopeError;
function assertSafeEventData(value, path = 'data') {
    if (typeof value === 'bigint' || value instanceof Uint8Array) {
        throw new InvalidEventEnvelopeError(`Event ${path} contains binary or non-serializable data; store large payloads in object storage`);
    }
    if (Array.isArray(value)) {
        value.forEach((item, index) => assertSafeEventData(item, `${path}[${index}]`));
        return;
    }
    if (value !== null && typeof value === 'object') {
        for (const [key, child] of Object.entries(value)) {
            if (FORBIDDEN_KEYS.has(key.toLowerCase())) {
                throw new InvalidEventEnvelopeError(`Event ${path}.${key} contains a forbidden secret field`);
            }
            assertSafeEventData(child, `${path}.${key}`);
        }
    }
}
function validateEventEnvelope(envelope) {
    const requiredStrings = [
        'eventId',
        'eventType',
        'producer',
        'tenantId',
        'correlationId',
        'traceId',
    ];
    for (const key of requiredStrings) {
        if (typeof envelope[key] !== 'string' || envelope[key].trim() === '') {
            throw new InvalidEventEnvelopeError(`${String(key)} must be a non-empty string`);
        }
    }
    if (!Number.isInteger(envelope.eventVersion) || envelope.eventVersion < 1) {
        throw new InvalidEventEnvelopeError('eventVersion must be a positive integer');
    }
    if (Number.isNaN(Date.parse(envelope.occurredAt))) {
        throw new InvalidEventEnvelopeError('occurredAt must be a valid ISO timestamp');
    }
    if (!envelope.actor?.id || !['user', 'service', 'system'].includes(envelope.actor.type)) {
        throw new InvalidEventEnvelopeError('actor must contain an id and a supported type');
    }
    if (!envelope.aggregate?.type || !envelope.aggregate.id) {
        throw new InvalidEventEnvelopeError('aggregate must contain a type and id');
    }
    assertSafeEventData(envelope.data);
    const bytes = Buffer.byteLength(JSON.stringify(envelope), 'utf8');
    if (bytes > MAX_EVENT_BYTES) {
        throw new InvalidEventEnvelopeError(`Event payload exceeds ${MAX_EVENT_BYTES} bytes; use object storage for large payloads`);
    }
    return envelope;
}
function createEventEnvelope(input) {
    const envelope = {
        eventId: input.eventId ?? (0, node_crypto_1.randomUUID)(),
        eventType: input.eventType,
        eventVersion: input.eventVersion,
        occurredAt: input.occurredAt ?? new Date().toISOString(),
        producer: input.producer,
        tenantId: input.tenantId,
        actor: input.actor,
        correlationId: input.correlationId,
        traceId: input.traceId,
        aggregate: input.aggregate,
        data: input.data,
    };
    return validateEventEnvelope(envelope);
}
function serializeEventEnvelope(envelope) {
    return JSON.stringify(validateEventEnvelope(envelope));
}
function parseEventEnvelope(payload) {
    let parsed;
    try {
        parsed = JSON.parse(payload);
    }
    catch {
        throw new InvalidEventEnvelopeError('Event payload must be valid JSON');
    }
    return validateEventEnvelope(parsed);
}
//# sourceMappingURL=index.js.map