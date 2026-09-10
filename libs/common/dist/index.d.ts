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
//# sourceMappingURL=index.d.ts.map