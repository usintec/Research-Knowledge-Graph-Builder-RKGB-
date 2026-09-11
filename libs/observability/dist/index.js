"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ObservabilityLogger = exports.JsonConsoleLogSink = exports.CorrelationContextStore = void 0;
exports.createTraceMetadata = createTraceMetadata;
exports.traceMetadataFromHeaders = traceMetadataFromHeaders;
exports.traceMetadataToHeaders = traceMetadataToHeaders;
const node_async_hooks_1 = require("node:async_hooks");
const node_crypto_1 = require("node:crypto");
function createTraceMetadata(correlationId = (0, node_crypto_1.randomUUID)(), traceId = (0, node_crypto_1.randomUUID)().replaceAll('-', ''), values = {}) {
    return { correlationId, traceId, ...values };
}
function traceMetadataFromHeaders(headers) {
    const header = (name) => {
        const value = headers[name] ?? headers[name.toLowerCase()];
        return Array.isArray(value) ? value[0] : value;
    };
    const values = {};
    const tenantId = header('x-tenant-id');
    const actorId = header('x-actor-id');
    if (tenantId) {
        values.tenantId = tenantId;
    }
    if (actorId) {
        values.actorId = actorId;
    }
    return createTraceMetadata(header('x-correlation-id') ?? (0, node_crypto_1.randomUUID)(), header('x-trace-id') ?? (0, node_crypto_1.randomUUID)().replaceAll('-', ''), values);
}
function traceMetadataToHeaders(metadata) {
    return {
        'x-correlation-id': metadata.correlationId,
        'x-trace-id': metadata.traceId,
        ...(metadata.tenantId ? { 'x-tenant-id': metadata.tenantId } : {}),
        ...(metadata.actorId ? { 'x-actor-id': metadata.actorId } : {}),
    };
}
class CorrelationContextStore {
    storage = new node_async_hooks_1.AsyncLocalStorage();
    get() {
        return this.storage.getStore();
    }
    run(metadata, callback) {
        return this.storage.run(metadata, callback);
    }
    async runAsync(metadata, callback) {
        return this.storage.run(metadata, callback);
    }
}
exports.CorrelationContextStore = CorrelationContextStore;
class JsonConsoleLogSink {
    write(record) {
        process.stdout.write(`${JSON.stringify(record)}\n`);
    }
}
exports.JsonConsoleLogSink = JsonConsoleLogSink;
class ObservabilityLogger {
    service;
    context;
    sink;
    constructor(service, context = new CorrelationContextStore(), sink = new JsonConsoleLogSink()) {
        this.service = service;
        this.context = context;
        this.sink = sink;
    }
    debug(message, attributes) {
        this.write('debug', message, attributes);
    }
    info(message, attributes) {
        this.write('info', message, attributes);
    }
    warn(message, attributes) {
        this.write('warn', message, attributes);
    }
    error(message, error, attributes) {
        this.write('error', message, attributes, error);
    }
    write(level, message, attributes, error) {
        const metadata = this.context.get();
        const normalizedError = error instanceof Error
            ? {
                name: error.name,
                message: error.message,
                ...(error.stack ? { stack: error.stack } : {}),
            }
            : undefined;
        const record = {
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
exports.ObservabilityLogger = ObservabilityLogger;
//# sourceMappingURL=index.js.map