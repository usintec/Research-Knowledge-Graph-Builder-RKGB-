export interface EventEnvelope<TData = unknown> {
  eventId: string;
  eventType: string;
  eventVersion: number;
  occurredAt: string;
  producer: string;
  correlationId: string;
  aggregate: string;
  data: TData;
}
