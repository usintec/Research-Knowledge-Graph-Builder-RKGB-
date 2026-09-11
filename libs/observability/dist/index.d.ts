export interface CorrelationTraceMetadata {
    correlationId: string;
    traceId: string;
    spanId?: string;
    tenantId?: string;
    actorId?: string;
    baggage?: Record<string, string>;
}
export type TraceContext = CorrelationTraceMetadata;
export declare function createTraceMetadata(correlationId?: string, traceId?: string, values?: Omit<CorrelationTraceMetadata, 'correlationId' | 'traceId'>): CorrelationTraceMetadata;
export declare function traceMetadataFromHeaders(headers: Record<string, string | string[] | undefined>): CorrelationTraceMetadata;
export declare function traceMetadataToHeaders(metadata: CorrelationTraceMetadata): Record<string, string>;
export declare class CorrelationContextStore {
    private readonly storage;
    get(): CorrelationTraceMetadata | undefined;
    run<T>(metadata: CorrelationTraceMetadata, callback: () => T): T;
    runAsync<T>(metadata: CorrelationTraceMetadata, callback: () => Promise<T>): Promise<T>;
}
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';
export interface LogRecord {
    timestamp: string;
    level: LogLevel;
    service: string;
    message: string;
    metadata?: CorrelationTraceMetadata;
    attributes?: Record<string, string | number | boolean | null>;
    error?: {
        name: string;
        message: string;
        stack?: string;
    };
}
export interface LogSink {
    write(record: LogRecord): void;
}
export declare class JsonConsoleLogSink implements LogSink {
    write(record: LogRecord): void;
}
export declare class ObservabilityLogger {
    private readonly service;
    private readonly context;
    private readonly sink;
    constructor(service: string, context?: CorrelationContextStore, sink?: LogSink);
    debug(message: string, attributes?: Record<string, string | number | boolean | null>): void;
    info(message: string, attributes?: Record<string, string | number | boolean | null>): void;
    warn(message: string, attributes?: Record<string, string | number | boolean | null>): void;
    error(message: string, error?: unknown, attributes?: Record<string, string | number | boolean | null>): void;
    private write;
}
//# sourceMappingURL=index.d.ts.map