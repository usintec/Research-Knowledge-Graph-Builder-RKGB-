"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KafkaEventConsumer = exports.InMemoryIdempotencyStore = exports.KafkaEventPublisher = exports.KafkaConnection = void 0;
exports.kafkaConfigFromEnv = kafkaConfigFromEnv;
exports.buildTopicName = buildTopicName;
exports.buildRetryTopicName = buildRetryTopicName;
exports.buildDeadLetterTopicName = buildDeadLetterTopicName;
exports.kafkaHealth = kafkaHealth;
const kafkajs_1 = require("kafkajs");
const common_1 = require("@rkgb/common");
function kafkaConfigFromEnv(source = process.env, serviceName = (0, common_1.envString)('SERVICE_NAME', 'rkgb-service', source)) {
    const brokers = (0, common_1.envString)('KAFKA_BROKERS', 'localhost:9092', source)
        .split(',')
        .map((broker) => broker.trim())
        .filter(Boolean);
    if (brokers.length === 0) {
        throw new common_1.ConfigurationError('KAFKA_BROKERS must contain at least one broker');
    }
    return {
        brokers,
        clientId: (0, common_1.envString)('KAFKA_CLIENT_ID', serviceName, source),
        groupId: (0, common_1.envString)('KAFKA_GROUP_ID', `${serviceName}.consumer`, source),
        connectionTimeoutMs: (0, common_1.envNumber)('KAFKA_CONNECTION_TIMEOUT_MS', 10_000, source),
        requestTimeoutMs: (0, common_1.envNumber)('KAFKA_REQUEST_TIMEOUT_MS', 30_000, source),
        retryAttempts: (0, common_1.envNumber)('KAFKA_RETRY_ATTEMPTS', 5, source),
        retryBackoffMs: (0, common_1.envNumber)('KAFKA_RETRY_BACKOFF_MS', 300, source),
        topicPrefix: (0, common_1.envString)('KAFKA_TOPIC_PREFIX', 'rkgb', source),
        deadLetterSuffix: (0, common_1.envString)('KAFKA_DLQ_SUFFIX', '.dlq', source),
        retrySuffix: (0, common_1.envString)('KAFKA_RETRY_SUFFIX', '.retry', source),
    };
}
function topicPart(value) {
    const normalized = value.trim().toLowerCase().replace(/[^a-z0-9._-]+/g, '-');
    if (!normalized) {
        throw new common_1.ConfigurationError('Kafka topic segments must not be empty');
    }
    return normalized;
}
function buildTopicName(config, input) {
    const version = input.version === undefined ? '' : `.v${input.version}`;
    return `${topicPart(config.topicPrefix)}.${topicPart(input.domain)}.${topicPart(input.event)}${version}`;
}
function buildRetryTopicName(config, topic) {
    return `${topicPart(topic)}${config.retrySuffix}`;
}
function buildDeadLetterTopicName(config, topic) {
    return `${topicPart(topic)}${config.deadLetterSuffix}`;
}
class KafkaJsFactory {
    client;
    constructor(client) {
        this.client = client;
    }
    producer() {
        const producer = this.client.producer();
        return {
            connect: () => producer.connect(),
            send: async (input) => {
                await producer.send({
                    topic: input.topic,
                    messages: input.messages.map((message) => ({
                        value: message.value,
                        ...(message.key !== undefined ? { key: message.key } : {}),
                        ...(message.headers ? { headers: message.headers } : {}),
                    })),
                });
            },
            disconnect: () => producer.disconnect(),
        };
    }
    consumer(groupId) {
        const consumer = this.client.consumer({ groupId });
        return {
            connect: () => consumer.connect(),
            subscribe: (input) => consumer.subscribe(input),
            run: (input) => consumer.run({
                eachMessage: async (payload) => {
                    const headers = {};
                    for (const [key, value] of Object.entries(payload.message.headers ?? {})) {
                        headers[key] = Array.isArray(value)
                            ? value[0]?.toString()
                            : value?.toString();
                    }
                    await input.eachMessage({
                        topic: payload.topic,
                        partition: payload.partition,
                        message: {
                            key: payload.message.key,
                            value: payload.message.value,
                            headers,
                        },
                    });
                },
            }),
            disconnect: () => consumer.disconnect(),
        };
    }
}
class KafkaConnection {
    config;
    factory;
    producerClient;
    consumerClients = new Set();
    connected = false;
    constructor(config, factory = new KafkaJsFactory(new kafkajs_1.Kafka({
        brokers: config.brokers,
        clientId: config.clientId,
        connectionTimeout: config.connectionTimeoutMs,
        requestTimeout: config.requestTimeoutMs,
        retry: {
            retries: config.retryAttempts,
            initialRetryTime: config.retryBackoffMs,
        },
    }))) {
        this.config = config;
        this.factory = factory;
    }
    async connectProducer() {
        if (!this.producerClient) {
            this.producerClient = this.factory.producer();
        }
        await this.producerClient.connect();
        this.connected = true;
        return this.producerClient;
    }
    async createConsumer(groupId = this.config.groupId) {
        const consumer = this.factory.consumer(groupId);
        await consumer.connect();
        this.consumerClients.add(consumer);
        this.connected = true;
        return consumer;
    }
    async disconnect() {
        const clients = [
            ...(this.producerClient ? [this.producerClient] : []),
            ...this.consumerClients,
        ];
        await Promise.all(clients.map((client) => client.disconnect()));
        this.consumerClients.clear();
        this.producerClient = undefined;
        this.connected = false;
    }
    isConnected() {
        return this.connected;
    }
    async health() {
        if (!this.connected) {
            throw new Error('Kafka connection is not established');
        }
    }
}
exports.KafkaConnection = KafkaConnection;
class KafkaEventPublisher {
    producer;
    connection;
    constructor(producer, connection) {
        this.producer = producer;
        this.connection = connection;
    }
    async publish(topic, event) {
        if (!this.connection.isConnected()) {
            throw new Error('Kafka producer is not connected');
        }
        await this.producer.send({
            topic,
            messages: [
                {
                    key: event.aggregate.id,
                    value: JSON.stringify(event),
                    headers: {
                        'event-type': event.eventType,
                        'event-version': String(event.eventVersion),
                        'correlation-id': event.correlationId,
                        'trace-id': event.traceId,
                    },
                },
            ],
        });
    }
}
exports.KafkaEventPublisher = KafkaEventPublisher;
class InMemoryIdempotencyStore {
    processed = new Set();
    async has(key) {
        return this.processed.has(key);
    }
    async mark(key) {
        this.processed.add(key);
    }
}
exports.InMemoryIdempotencyStore = InMemoryIdempotencyStore;
class KafkaEventConsumer {
    options;
    running = false;
    constructor(options) {
        this.options = options;
    }
    async start(fromBeginning = false) {
        await this.options.consumer.subscribe({ topic: this.options.topic, fromBeginning });
        this.running = true;
        await this.options.consumer.run({
            eachMessage: async ({ message }) => {
                if (!message.value) {
                    return;
                }
                const event = JSON.parse(message.value.toString());
                if (await this.options.idempotency.has(event.eventId)) {
                    return;
                }
                try {
                    await this.options.handler(event);
                    await this.options.idempotency.mark(event.eventId);
                }
                catch (error) {
                    await this.publishFailure(event, error);
                    throw error;
                }
            },
        });
    }
    async stop() {
        if (this.running) {
            await this.options.consumer.disconnect();
            this.running = false;
        }
    }
    isRunning() {
        return this.running;
    }
    async publishFailure(event, error) {
        if (!this.options.publisher || !this.options.config) {
            return;
        }
        const attempts = this.options.maxAttempts ?? 3;
        const topic = buildDeadLetterTopicName(this.options.config, attempts > 0 ? this.options.topic : buildRetryTopicName(this.options.config, this.options.topic));
        await this.options.publisher.publish(topic, {
            ...event,
            data: {
                originalEvent: event.data,
                failure: error instanceof Error ? error.message : 'Consumer handler failed',
            },
        });
    }
}
exports.KafkaEventConsumer = KafkaEventConsumer;
function kafkaHealth(connection, config) {
    return {
        connected: connection.isConnected(),
        clientId: config.clientId,
        brokers: config.brokers,
    };
}
//# sourceMappingURL=index.js.map