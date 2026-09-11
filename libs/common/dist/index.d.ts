import { ArgumentsHost, ExceptionFilter, LoggerService, NestMiddleware } from '@nestjs/common';
import type { NextFunction, Request, Response } from 'express';
export interface HealthResponse {
    service: string;
    status: 'ok' | 'ready';
    timestamp: string;
}
export declare function createHealthController(serviceName: string): {
    new (): {
        health(): HealthResponse;
        readiness(): HealthResponse;
    };
};
export declare class CorrelationIdMiddleware implements NestMiddleware {
    use(request: Request, response: Response, next: NextFunction): void;
}
export declare class StructuredLogger implements LoggerService {
    private readonly serviceName;
    constructor(serviceName: string);
    log(message: unknown, context?: string): void;
    error(message: unknown, trace?: string, context?: string): void;
    warn(message: unknown, context?: string): void;
    debug(message: unknown, context?: string): void;
    verbose(message: unknown, context?: string): void;
    private write;
}
export declare class CommonHttpExceptionFilter implements ExceptionFilter {
    catch(exception: unknown, host: ArgumentsHost): void;
}
export type ErrorDetails = Record<string, unknown>;
export declare class RkgbError extends Error {
    readonly code: string;
    readonly statusCode: number;
    readonly details?: ErrorDetails | undefined;
    constructor(message: string, code: string, statusCode?: number, details?: ErrorDetails | undefined);
}
export declare class ConfigurationError extends RkgbError {
    constructor(message: string, details?: ErrorDetails);
}
export declare class DependencyUnavailableError extends RkgbError {
    constructor(dependency: string, details?: ErrorDetails);
}
export declare function requiredEnv(name: string, source?: NodeJS.ProcessEnv): string;
export declare function envString(name: string, fallback: string, source?: NodeJS.ProcessEnv): string;
export declare function envNumber(name: string, fallback: number, source?: NodeJS.ProcessEnv): number;
export declare function envBoolean(name: string, fallback: boolean, source?: NodeJS.ProcessEnv): boolean;
export declare function validateRequiredConfig(values: Record<string, string | number | boolean | undefined>, required: readonly string[]): void;
export interface HealthCheckResult {
    name: string;
    status: 'up' | 'down';
    checkedAt: string;
    latencyMs: number;
    message?: string;
    details?: Record<string, unknown>;
}
export type HealthCheck = () => Promise<void> | void;
export interface ReadinessReport {
    status: 'ready' | 'not_ready';
    checkedAt: string;
    checks: HealthCheckResult[];
}
export declare class HealthCheckRegistry {
    private readonly checks;
    register(name: string, check: HealthCheck): this;
    run(): Promise<HealthCheckResult[]>;
    readiness(): Promise<ReadinessReport>;
}
//# sourceMappingURL=index.d.ts.map