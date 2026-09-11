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
export declare class InvalidEventEnvelopeError extends Error {
    constructor(message: string);
}
export declare function assertSafeEventData(value: unknown, path?: string): void;
export declare function validateEventEnvelope<TData>(envelope: EventEnvelope<TData>): EventEnvelope<TData>;
export declare function createEventEnvelope<TData>(input: EventEnvelopeInput<TData>): EventEnvelope<TData>;
export declare function serializeEventEnvelope<TData>(envelope: EventEnvelope<TData>): string;
export declare function parseEventEnvelope<TData>(payload: string): EventEnvelope<TData>;
//# sourceMappingURL=index.d.ts.map