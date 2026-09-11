import { randomUUID } from 'node:crypto';

export interface EventActor {
  id: string;
  type: 'user' | 'service' | 'system';
}

export interface AggregateReference {
  type: string;
  id: string;
}

export interface EventEnvelope<TData = unknown> {
  eventId: string;
  eventType: string;
  eventVersion: number;
  occurredAt: string;
  producer: string;
  tenantId: string;
  actor: EventActor;
  correlationId: string;
  traceId: string;
  aggregate: AggregateReference;
  data: TData;
}

export interface EventEnvelopeInput<TData> {
  eventType: string;
  eventVersion: number;
  producer: string;
  tenantId: string;
  actor: EventActor;
  correlationId: string;
  traceId: string;
  aggregate: AggregateReference;
  data: TData;
  eventId?: string;
  occurredAt?: string;
}

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

export class InvalidEventEnvelopeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidEventEnvelopeError';
  }
}

export function assertSafeEventData(value: unknown, path = 'data'): void {
  if (typeof value === 'bigint' || value instanceof Uint8Array) {
    throw new InvalidEventEnvelopeError(
      `Event ${path} contains binary or non-serializable data; store large payloads in object storage`,
    );
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

export function validateEventEnvelope<TData>(
  envelope: EventEnvelope<TData>,
): EventEnvelope<TData> {
  const requiredStrings: Array<keyof EventEnvelope<TData>> = [
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
    throw new InvalidEventEnvelopeError(
      `Event payload exceeds ${MAX_EVENT_BYTES} bytes; use object storage for large payloads`,
    );
  }
  return envelope;
}

export function createEventEnvelope<TData>(
  input: EventEnvelopeInput<TData>,
): EventEnvelope<TData> {
  const envelope: EventEnvelope<TData> = {
    eventId: input.eventId ?? randomUUID(),
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

export function serializeEventEnvelope<TData>(envelope: EventEnvelope<TData>): string {
  return JSON.stringify(validateEventEnvelope(envelope));
}

export function parseEventEnvelope<TData>(payload: string): EventEnvelope<TData> {
  let parsed: unknown;
  try {
    parsed = JSON.parse(payload);
  } catch {
    throw new InvalidEventEnvelopeError('Event payload must be valid JSON');
  }
  return validateEventEnvelope(parsed as EventEnvelope<TData>);
}