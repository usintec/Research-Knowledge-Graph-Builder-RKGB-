import { createHealthController } from './index';

describe('health controller factory', () => {
  it('returns service health and readiness responses', () => {
    const controller = new (createHealthController('test-service'))();

    expect(controller.health()).toMatchObject({ service: 'test-service', status: 'ok' });
    expect(controller.readiness()).toMatchObject({ service: 'test-service', status: 'ready' });
  });
});
