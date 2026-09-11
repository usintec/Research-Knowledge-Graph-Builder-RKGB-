import { createEventEnvelope } from '@rkgb/events';
import {
  InMemoryIdempotencyStore,
  KafkaConnection,
  KafkaEventConsumer,
  KafkaEventPublisher,
  type KafkaConsumerLike,
  type KafkaFactory,
  type KafkaProducerLike,
  buildDeadLetterTopicName,
  buildTopicName,
  kafkaConfigFromEnv,
} from './index';

class FakeProducer implements KafkaProducerLike {
  readonly messages: Array<{ topic: string; messages: Array<{ value: string }> }> = [];
  connected = false;

  async connect(): Promise<void> {
    this.connected = true;
  }

  async send(input: { topic: string; messages: Array<{ value: string }> }): Promise<void> {
    this.messages.push(input);
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }
}

class FakeConsumer implements KafkaConsumerLike {
  handler?: (message: {
    topic: string;
    partition: number;
    message: { value?: Buffer | null };
  }) => Promise<void>;
  connected = false;

  async connect(): Promise<void> {
    this.connected = true;
  }

  async subscribe(): Promise<void> {}

  async run(input: {
    eachMessage: (message: {
      topic: string;
      partition: number;
      message: { value?: Buffer | null };
    }) => Promise<void>;
  }): Promise<void> {
    this.handler = input.eachMessage;
  }

  async disconnect(): Promise<void> {
    this.connected = false;
  }
}

describe('Kafka shared infrastructure', () => {
  it('builds explicit client/group configuration and topic names', () => {
    const config = kafkaConfigFromEnv(
      {
        KAFKA_BROKERS: 'kafka-1:9092,kafka-2:9092',
        KAFKA_CLIENT_ID: 'document-service',
        KAFKA_GROUP_ID: 'document-service.consumer',
      },
      'document-service',
    );
    expect(config.brokers).toEqual(['kafka-1:9092', 'kafka-2:9092']);
    expect(buildTopicName(config, { domain: 'documents', event: 'created', version: 1 })).toBe(
      'rkgb.documents.created.v1',
    );
    expect(buildDeadLetterTopicName(config, 'rkgb.documents.created.v1')).toBe(
      'rkgb.documents.created.v1.dlq',
    );
  });

  it('publishes an event with routing headers', async () => {
    const producer = new FakeProducer();
    const config = kafkaConfigFromEnv();
    const connection = new KafkaConnection(config, {
      producer: () => producer,
      consumer: () => new FakeConsumer(),
    } satisfies KafkaFactory);
    await connection.connectProducer();
    const publisher = new KafkaEventPublisher(producer, connection);
    const event = createEventEnvelope({
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
    const connection = new KafkaConnection(kafkaConfigFromEnv(), {
      producer: () => new FakeProducer(),
      consumer: () => consumer,
    } satisfies KafkaFactory);
    await connection.createConsumer();
    const event = createEventEnvelope({
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
    const store = new InMemoryIdempotencyStore();
    let count = 0;
    const eventConsumer = new KafkaEventConsumer({
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