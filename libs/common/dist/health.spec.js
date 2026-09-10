"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("./index");
describe('health controller factory', () => {
    it('returns service health and readiness responses', () => {
        const controller = new ((0, index_1.createHealthController)('test-service'))();
        expect(controller.health()).toMatchObject({ service: 'test-service', status: 'ok' });
        expect(controller.readiness()).toMatchObject({ service: 'test-service', status: 'ready' });
    });
});
//# sourceMappingURL=health.spec.js.map