import {
  ConfigurationError,
  HealthCheckRegistry,
  envBoolean,
  envNumber,
  requiredEnv,
} from './index';

describe('shared infrastructure primitives', () => {
  it('parses validated environment values', () => {
    const source = { FLAG: 'true', PORT: '5432', REQUIRED: 'value' };
    expect(envBoolean('FLAG', false, source)).toBe(true);
    expect(envNumber('PORT', 0, source)).toBe(5432);
    expect(requiredEnv('REQUIRED', source)).toBe('value');
  });

  it('rejects malformed environment values', () => {
    expect(() => envBoolean('FLAG', false, { FLAG: 'sometimes' })).toThrow(ConfigurationError);
    expect(() => envNumber('PORT', 0, { PORT: 'not-a-number' })).toThrow(ConfigurationError);
    expect(() => requiredEnv('MISSING', {})).toThrow(ConfigurationError);
  });

  it('reports readiness only when every check is healthy', async () => {
    const registry = new HealthCheckRegistry()
      .register('postgres', () => undefined)
      .register('redis', () => {
        throw new Error('connection refused');
      });

    const report = await registry.readiness();
    expect(report.status).toBe('not_ready');
    expect(report.checks).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ name: 'postgres', status: 'up' }),
        expect.objectContaining({ name: 'redis', status: 'down', message: 'connection refused' }),
      ]),
    );
  });
});