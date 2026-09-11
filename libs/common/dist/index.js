"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.HealthCheckRegistry = exports.DependencyUnavailableError = exports.ConfigurationError = exports.RkgbError = exports.CommonHttpExceptionFilter = exports.StructuredLogger = exports.CorrelationIdMiddleware = void 0;
exports.createHealthController = createHealthController;
exports.requiredEnv = requiredEnv;
exports.envString = envString;
exports.envNumber = envNumber;
exports.envBoolean = envBoolean;
exports.validateRequiredConfig = validateRequiredConfig;
const common_1 = require("@nestjs/common");
const node_crypto_1 = require("node:crypto");
function createHealthController(serviceName) {
    let HealthController = class HealthController {
        health() {
            return {
                service: serviceName,
                status: 'ok',
                timestamp: new Date().toISOString(),
            };
        }
        readiness() {
            return {
                service: serviceName,
                status: 'ready',
                timestamp: new Date().toISOString(),
            };
        }
    };
    __decorate([
        (0, common_1.Get)('health'),
        __metadata("design:type", Function),
        __metadata("design:paramtypes", []),
        __metadata("design:returntype", Object)
    ], HealthController.prototype, "health", null);
    __decorate([
        (0, common_1.Get)('ready'),
        __metadata("design:type", Function),
        __metadata("design:paramtypes", []),
        __metadata("design:returntype", Object)
    ], HealthController.prototype, "readiness", null);
    HealthController = __decorate([
        (0, common_1.Controller)()
    ], HealthController);
    return HealthController;
}
let CorrelationIdMiddleware = class CorrelationIdMiddleware {
    use(request, response, next) {
        const correlationId = request.header('x-correlation-id') ?? (0, node_crypto_1.randomUUID)();
        response.setHeader('x-correlation-id', correlationId);
        request.headers['x-correlation-id'] = correlationId;
        next();
    }
};
exports.CorrelationIdMiddleware = CorrelationIdMiddleware;
exports.CorrelationIdMiddleware = CorrelationIdMiddleware = __decorate([
    (0, common_1.Injectable)()
], CorrelationIdMiddleware);
class StructuredLogger {
    serviceName;
    constructor(serviceName) {
        this.serviceName = serviceName;
    }
    log(message, context) {
        this.write('info', message, context);
    }
    error(message, trace, context) {
        this.write('error', message, context, trace);
    }
    warn(message, context) {
        this.write('warn', message, context);
    }
    debug(message, context) {
        this.write('debug', message, context);
    }
    verbose(message, context) {
        this.write('trace', message, context);
    }
    write(level, message, context, trace) {
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
exports.StructuredLogger = StructuredLogger;
let CommonHttpExceptionFilter = class CommonHttpExceptionFilter {
    catch(exception, host) {
        const response = host.switchToHttp().getResponse();
        const status = exception instanceof common_1.HttpException ? exception.getStatus() : 500;
        const message = exception instanceof common_1.HttpException ? exception.getResponse() : 'Internal server error';
        response.status(status).json({
            statusCode: status,
            message,
            timestamp: new Date().toISOString(),
        });
    }
};
exports.CommonHttpExceptionFilter = CommonHttpExceptionFilter;
exports.CommonHttpExceptionFilter = CommonHttpExceptionFilter = __decorate([
    (0, common_1.Catch)()
], CommonHttpExceptionFilter);
class RkgbError extends Error {
    code;
    statusCode;
    details;
    constructor(message, code, statusCode = 500, details) {
        super(message);
        this.code = code;
        this.statusCode = statusCode;
        this.details = details;
        this.name = 'RkgbError';
    }
}
exports.RkgbError = RkgbError;
class ConfigurationError extends RkgbError {
    constructor(message, details) {
        super(message, 'CONFIGURATION_ERROR', 500, details);
        this.name = 'ConfigurationError';
    }
}
exports.ConfigurationError = ConfigurationError;
class DependencyUnavailableError extends RkgbError {
    constructor(dependency, details) {
        super(`${dependency} is unavailable`, 'DEPENDENCY_UNAVAILABLE', 503, details);
        this.name = 'DependencyUnavailableError';
    }
}
exports.DependencyUnavailableError = DependencyUnavailableError;
function requiredEnv(name, source = process.env) {
    const value = source[name]?.trim();
    if (!value) {
        throw new ConfigurationError(`Missing required environment variable: ${name}`, {
            variable: name,
        });
    }
    return value;
}
function envString(name, fallback, source = process.env) {
    return source[name]?.trim() || fallback;
}
function envNumber(name, fallback, source = process.env) {
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
function envBoolean(name, fallback, source = process.env) {
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
function validateRequiredConfig(values, required) {
    const missing = required.filter((key) => values[key] === undefined || values[key] === '');
    if (missing.length > 0) {
        throw new ConfigurationError(`Missing required configuration: ${missing.join(', ')}`, {
            missing,
        });
    }
}
class HealthCheckRegistry {
    checks = new Map();
    register(name, check) {
        if (this.checks.has(name)) {
            throw new ConfigurationError(`Health check already registered: ${name}`, { name });
        }
        this.checks.set(name, check);
        return this;
    }
    async run() {
        const results = [];
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
            }
            catch (error) {
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
    async readiness() {
        const checks = await this.run();
        return {
            status: checks.every((check) => check.status === 'up') ? 'ready' : 'not_ready',
            checkedAt: new Date().toISOString(),
            checks,
        };
    }
}
exports.HealthCheckRegistry = HealthCheckRegistry;
//# sourceMappingURL=index.js.map