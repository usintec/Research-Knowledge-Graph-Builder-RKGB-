"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const events_1 = require("@rkgb/events");
const index_1 = require("./index");
class FakeProducer {
    messages = [];
    connected = false;
    async connect() {
        this.connected = true;
    }
    async send(input) {
        this.messages.push(input);
    }
    async disconnect() {
        this.connected = false;
    }
}
class FakeConsumer {
    handler;
    connected = false;
    async connect() {
        this.connected = true;
    }
    async subscribe() { }
    async run(input) {
        this.handler = input.eachMessage;
    }
    async disconnect() {
        this.connected = false;
    }
}
describe('Kafka shared infrastructure', () => {
    it('builds explicit client/group configuration and topic names', () => {
        const config = (0, index_1.kafkaConfigFromEnv)({
            KAFKA_BROKERS: 'kafka-1:9092,kafka-2:9092',
            KAFKA_CLIENT_ID: 'document-service',
            KAFKA_GROUP_ID: 'document-service.consumer',
        }, 'document-service');
        expect(config.brokers).toEqual(['kafka-1:9092', 'kafka-2:9092']);
        expect((0, index_1.buildTopicName)(config, { domain: 'documents', event: 'created', version: 1 })).toBe('rkgb.documents.created.v1');
        expect((0, index_1.buildDeadLetterTopicName)(config, 'rkgb.documents.created.v1')).toBe('rkgb.documents.created.v1.dlq');
    });
    it('publishes an event with routing headers', async () => {
        const producer = new FakeProducer();
        const config = (0, index_1.kafkaConfigFromEnv)();
        const connection = new index_1.KafkaConnection(config, {
            producer: () => producer,
            consumer: () => new FakeConsumer(),
        });
        await connection.connectProducer();
        const publisher = new index_1.KafkaEventPublisher(producer, connection);
        const event = (0, events_1.createEventEnvelope)({
            eventType: 'document.created',
            eventVersion: 1,
            producer: 'document-service',
            tenantId: 'tenant',
            actor: { id: 'system', type: 'service' },
            correlationId: 'corr',
            traceId: 'trace',
            aggregate: { type: 'document', id: 'doc' },
            data: { objectKey: 'doc' },
        });
        await publisher.publish('rkgb.documents.created.v1', event);
        expect(producer.messages[0]?.topic).toBe('rkgb.documents.created.v1');
        expect(JSON.parse(producer.messages[0]?.messages[0]?.value ?? '{}')).toMatchObject({
            eventId: event.eventId,
        });
    });
    it('does not process an event twice', async () => {
        const consumer = new FakeConsumer();
        const connection = new index_1.KafkaConnection((0, index_1.kafkaConfigFromEnv)(), {
            producer: () => new FakeProducer(),
            consumer: () => consumer,
        });
        await connection.createConsumer();
        const event = (0, events_1.createEventEnvelope)({
            eventType: 'document.created',
            eventVersion: 1,
            producer: 'document-service',
            tenantId: 'tenant',
            actor: { id: 'system', type: 'service' },
            correlationId: 'corr',
            traceId: 'trace',
            aggregate: { type: 'document', id: 'doc' },
            data: {},
        });
        const store = new index_1.InMemoryIdempotencyStore();
        let count = 0;
        const eventConsumer = new index_1.KafkaEventConsumer({
            topic: 'rkgb.documents.created.v1',
            consumer,
            idempotency: store,
            handler: async () => {
                count += 1;
            },
        });
        await eventConsumer.start();
        await consumer.handler?.({
            topic: 'rkgb.documents.created.v1',
            partition: 0,
            message: { value: Buffer.from(JSON.stringify(event)) },
        });
        await consumer.handler?.({
            topic: 'rkgb.documents.created.v1',
            partition: 0,
            message: { value: Buffer.from(JSON.stringify(event)) },
        });
        expect(count).toBe(1);
    });
});
//# sourceMappingURL=kafka.spec.js.map