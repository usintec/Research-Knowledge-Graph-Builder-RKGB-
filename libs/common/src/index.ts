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
