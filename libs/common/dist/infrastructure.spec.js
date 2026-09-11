"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("./index");
describe('shared infrastructure primitives', () => {
    it('parses validated environment values', () => {
        const source = { FLAG: 'true', PORT: '5432', REQUIRED: 'value' };
        expect((0, index_1.envBoolean)('FLAG', false, source)).toBe(true);
        expect((0, index_1.envNumber)('PORT', 0, source)).toBe(5432);
        expect((0, index_1.requiredEnv)('REQUIRED', source)).toBe('value');
    });
    it('rejects malformed environment values', () => {
        expect(() => (0, index_1.envBoolean)('FLAG', false, { FLAG: 'sometimes' })).toThrow(index_1.ConfigurationError);
        expect(() => (0, index_1.envNumber)('PORT', 0, { PORT: 'not-a-number' })).toThrow(index_1.ConfigurationError);
        expect(() => (0, index_1.requiredEnv)('MISSING', {})).toThrow(index_1.ConfigurationError);
    });
    it('reports readiness only when every check is healthy', async () => {
        const registry = new index_1.HealthCheckRegistry()
            .register('postgres', () => undefined)
            .register('redis', () => {
            throw new Error('connection refused');
        });
        const report = await registry.readiness();
        expect(report.status).toBe('not_ready');
        expect(report.checks).toEqual(expect.arrayContaining([
            expect.objectContaining({ name: 'postgres', status: 'up' }),
            expect.objectContaining({ name: 'redis', status: 'down', message: 'connection refused' }),
        ]));
    });
});
//# sourceMappingURL=infrastructure.spec.js.map