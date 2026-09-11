import {
  ArgumentsHost,
  Catch,
  Controller,
  ExceptionFilter,
  Get,
  HttpException,
  Injectable,
  LoggerService,
  NestMiddleware,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import type { NextFunction, Request, Response } from 'express';

export interface HealthResponse {
  service: string;
  status: 'ok' | 'ready';
  timestamp: string;
}

export function createHealthController(serviceName: string) {
  @Controller()
  class HealthController {
    @Get('health')
    health(): HealthResponse {
      return {
        service: serviceName,
        status: 'ok',
        timestamp: new Date().toISOString(),
      };
    }

    @Get('ready')
    readiness(): HealthResponse {
      return {
        service: serviceName,
        status: 'ready',
        timestamp: new Date().toISOString(),
      };
    }
  }

  return HealthController;
}

@Injectable()
export class CorrelationIdMiddleware implements NestMiddleware {
  use(request: Request, response: Response, next: NextFunction): void {
    const correlationId = request.header('x-correlation-id') ?? randomUUID();
    response.setHeader('x-correlation-id', correlationId);
    request.headers['x-correlation-id'] = correlationId;
    next();
  }
}

export class StructuredLogger implements LoggerService {
  constructor(private readonly serviceName: string) {}

  log(message: unknown, context?: string): void {
    this.write('info', message, context);
  }

  error(message: unknown, trace?: string, context?: string): void {
    this.write('error', message, context, trace);
  }

  warn(message: unknown, context?: string): void {
    this.write('warn', message, context);
  }

  debug(message: unknown, context?: string): void {
    this.write('debug', message, context);
  }

  verbose(message: unknown, context?: string): void {
    this.write('trace', message, context);
  }

  private write(level: string, message: unknown, context?: string, trace?: string): void {
    const record = {
      timestamp: new Date().toISOString(),
      level,
      service: this.serviceName,
      ...(context ? { context } : {}),
      message: String(message),
      ...(trace ? { trace } : {}),
    };
    process.stdout.write(`${JSON.stringify(record)}\n`);
  }
}

@Catch()
export class CommonHttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost): void {
    const response = host.switchToHttp().getResponse<Response>();
    const status = exception instanceof HttpException ? exception.getStatus() : 500;
    const message =
      exception instanceof HttpException ? exception.getResponse() : 'Internal server error';

    response.status(status).json({
      statusCode: status,
      message,
      timestamp: new Date().toISOString(),
    });
  }
}

export type ErrorDetails = Record<string, unknown>;

export class RkgbError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode = 500,
    public readonly details?: ErrorDetails,
  ) {
    super(message);
    this.name = 'RkgbError';
  }
}

export class ConfigurationError extends RkgbError {
  constructor(message: string, details?: ErrorDetails) {
    super(message, 'CONFIGURATION_ERROR', 500, details);
    this.name = 'ConfigurationError';
  }
}

export class DependencyUnavailableError extends RkgbError {
  constructor(dependency: string, details?: ErrorDetails) {
    super(`${dependency} is unavailable`, 'DEPENDENCY_UNAVAILABLE', 503, details);
    this.name = 'DependencyUnavailableError';
  }
}

export function requiredEnv(
  name: string,
  source: NodeJS.ProcessEnv = process.env,
): string {
  const value = source[name]?.trim();
  if (!value) {
    throw new ConfigurationError(`Missing required environment variable: ${name}`, {
      variable: name,
    });
  }
  return value;
}

export function envString(
  name: string,
  fallback: string,
  source: NodeJS.ProcessEnv = process.env,
): string {
  return source[name]?.trim() || fallback;
}

export function envNumber(
  name: string,
  fallback: number,
  source: NodeJS.ProcessEnv = process.env,
): number {
  const raw = source[name];
  if (raw === undefined || raw.trim() === '') {
    return fallback;
  }
  const value = Number(raw);
  if (!Number.isFinite(value)) {
    throw new ConfigurationError(`Environment variable ${name} must be a number`, {
      variable: name,
      value: raw,
    });
  }
  return value;
}

export function envBoolean(
  name: string,
  fallback: boolean,
  source: NodeJS.ProcessEnv = process.env,
): boolean {
  const raw = source[name]?.trim().toLowerCase();
  if (!raw) {
    return fallback;
  }
  if (['1', 'true', 'yes', 'on'].includes(raw)) {
    return true;
  }
  if (['0', 'false', 'no', 'off'].includes(raw)) {
    return false;
  }
  throw new ConfigurationError(`Environment variable ${name} must be boolean`, {
    variable: name,
    value: raw,
  });
}

export function validateRequiredConfig(
  values: Record<string, string | number | boolean | undefined>,
  required: readonly string[],
): void {
  const missing = required.filter((key) => values[key] === undefined || values[key] === '');
  if (missing.length > 0) {
    throw new ConfigurationError(`Missing required configuration: ${missing.join(', ')}`, {
      missing,
    });
  }
}

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

export class HealthCheckRegistry {
  private readonly checks = new Map<string, HealthCheck>();

  register(name: string, check: HealthCheck): this {
    if (this.checks.has(name)) {
      throw new ConfigurationError(`Health check already registered: ${name}`, { name });
    }
    this.checks.set(name, check);
    return this;
  }

  async run(): Promise<HealthCheckResult[]> {
    const results: HealthCheckResult[] = [];
    for (const [name, check] of this.checks) {
      const startedAt = performance.now();
      try {
        await check();
        results.push({
          name,
          status: 'up',
          checkedAt: new Date().toISOString(),
          latencyMs: Math.round((performance.now() - startedAt) * 100) / 100,
        });
      } catch (error) {
        results.push({
          name,
          status: 'down',
          checkedAt: new Date().toISOString(),
          latencyMs: Math.round((performance.now() - startedAt) * 100) / 100,
          message: error instanceof Error ? error.message : 'Health check failed',
        });
      }
    }
    return results;
  }

  async readiness(): Promise<ReadinessReport> {
    const checks = await this.run();
    return {
      status: checks.every((check) => check.status === 'up') ? 'ready' : 'not_ready',
      checkedAt: new Date().toISOString(),
      checks,
    };
  }
}
