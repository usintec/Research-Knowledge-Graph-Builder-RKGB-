import { AsyncLocalStorage } from 'node:async_hooks';
import { randomUUID } from 'node:crypto';

export interface CorrelationTraceMetadata {
  correlationId: string;
  traceId: string;
  spanId?: string;
  tenantId?: string;
  actorId?: string;
  baggage?: Record<string, string>;
}

export type TraceContext = CorrelationTraceMetadata;

export function createTraceMetadata(
  correlationId: string = randomUUID(),
  traceId: string = randomUUID().replaceAll('-', ''),
  values: Omit<CorrelationTraceMetadata, 'correlationId' | 'traceId'> = {},
): CorrelationTraceMetadata {
  return { correlationId, traceId, ...values };
}

export function traceMetadataFromHeaders(
  headers: Record<string, string | string[] | undefined>,
): CorrelationTraceMetadata {
  const header = (name: string): string | undefined => {
    const value = headers[name] ?? headers[name.toLowerCase()];
    return Array.isArray(value) ? value[0] : value;
  };

  const values: Omit<CorrelationTraceMetadata, 'correlationId' | 'traceId'> = {};
  const tenantId = header('x-tenant-id');
  const actorId = header('x-actor-id');
  if (tenantId) {
    values.tenantId = tenantId;
  }
  if (actorId) {
    values.actorId = actorId;
  }

  return createTraceMetadata(
    header('x-correlation-id') ?? randomUUID(),
    header('x-trace-id') ?? randomUUID().replaceAll('-', ''),
    values,
  );
}

export function traceMetadataToHeaders(
  metadata: CorrelationTraceMetadata,
): Record<string, string> {
  return {
    'x-correlation-id': metadata.correlationId,
    'x-trace-id': metadata.traceId,
    ...(metadata.tenantId ? { 'x-tenant-id': metadata.tenantId } : {}),
    ...(metadata.actorId ? { 'x-actor-id': metadata.actorId } : {}),
  };
}

export class CorrelationContextStore {
  private readonly storage = new AsyncLocalStorage<CorrelationTraceMetadata>();

  get(): CorrelationTraceMetadata | undefined {
    return this.storage.getStore();
  }

  run<T>(metadata: CorrelationTraceMetadata, callback: () => T): T {
    return this.storage.run(metadata, callback);
  }

  async runAsync<T>(
    metadata: CorrelationTraceMetadata,
    callback: () => Promise<T>,
  ): Promise<T> {
    return this.storage.run(metadata, callback);
  }
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

export interface LogRecord {
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
  metadata?: CorrelationTraceMetadata;
  attributes?: Record<string, string | number | boolean | null>;
  error?: { name: string; message: string; stack?: string };
}

export interface LogSink {
  write(record: LogRecord): void;
}

export class JsonConsoleLogSink implements LogSink {
  write(record: LogRecord): void {
    process.stdout.write(`${JSON.stringify(record)}\n`);
  }
}

export class ObservabilityLogger {
  constructor(
    private readonly service: string,
    private readonly context = new CorrelationContextStore(),
    private readonly sink: LogSink = new JsonConsoleLogSink(),
  ) {}

  debug(message: string, attributes?: Record<string, string | number | boolean | null>): void {
    this.write('debug', message, attributes);
  }

  info(message: string, attributes?: Record<string, string | number | boolean | null>): void {
    this.write('info', message, attributes);
  }

  warn(message: string, attributes?: Record<string, string | number | boolean | null>): void {
    this.write('warn', message, attributes);
  }

  error(
    message: string,
    error?: unknown,
    attributes?: Record<string, string | number | boolean | null>,
  ): void {
    this.write('error', message, attributes, error);
  }

  private write(
    level: LogLevel,
    message: string,
    attributes?: Record<string, string | number | boolean | null>,
    error?: unknown,
  ): void {
    const metadata = this.context.get();
    const normalizedError =
      error instanceof Error
        ? {
            name: error.name,
            message: error.message,
            ...(error.stack ? { stack: error.stack } : {}),
          }
        : undefined;
    const record: LogRecord = {
      timestamp: new Date().toISOString(),
      level,
      service: this.service,
      message,
      ...(metadata ? { metadata } : {}),
      ...(attributes ? { attributes } : {}),
      ...(normalizedError ? { error: normalizedError } : {}),
    };
    this.sink.write(record);
  }
}
