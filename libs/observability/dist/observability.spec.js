"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("./index");
describe('observability primitives', () => {
    it('round-trips correlation and trace metadata through headers', () => {
        const metadata = (0, index_1.createTraceMetadata)('corr-1', 'trace-1', {
            tenantId: 'tenant-1',
            actorId: 'actor-1',
        });
        const headers = (0, index_1.traceMetadataToHeaders)(metadata);
        expect((0, index_1.traceMetadataFromHeaders)(headers)).toMatchObject(metadata);
    });
    it('propagates context across async work', async () => {
        const store = new index_1.CorrelationContextStore();
        const metadata = (0, index_1.createTraceMetadata)('corr-async', 'trace-async');
        await store.runAsync(metadata, async () => {
            await Promise.resolve();
            expect(store.get()).toEqual(metadata);
        });
        expect(store.get()).toBeUndefined();
    });
});
//# sourceMappingURL=observability.spec.js.map