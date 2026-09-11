import { Kafka, type Consumer, type Producer } from 'kafkajs';
import { envNumber, envString, ConfigurationError } from '@rkgb/common';
import type { EventEnvelope } from '@rkgb/events';

export interface KafkaClientOptions {
  brokers: string[];
  clientId: string;
  groupId: string;
  connectionTimeoutMs: number;
  requestTimeoutMs: number;
  retryAttempts: number;
  retryBackoffMs: number;
  topicPrefix: string;
  deadLetterSuffix: string;
  retrySuffix: string;
}

export function kafkaConfigFromEnv(
  source: NodeJS.ProcessEnv = process.env,
  serviceName = envString('SERVICE_NAME', 'rkgb-service', source),
): KafkaClientOptions {
  const brokers = envString('KAFKA_BROKERS', 'localhost:9092', source)
    .split(',')
    .map((broker) => broker.trim())
    .filter(Boolean);
  if (brokers.length === 0) {
    throw new ConfigurationError('KAFKA_BROKERS must contain at least one broker');
  }
  return {
    brokers,
    clientId: envString('KAFKA_CLIENT_ID', serviceName, source),
    groupId: envString('KAFKA_GROUP_ID', `${serviceName}.consumer`, source),
    connectionTimeoutMs: envNumber('KAFKA_CONNECTION_TIMEOUT_MS', 10_000, source),
    requestTimeoutMs: envNumber('KAFKA_REQUEST_TIMEOUT_MS', 30_000, source),
    retryAttempts: envNumber('KAFKA_RETRY_ATTEMPTS', 5, source),
    retryBackoffMs: envNumber('KAFKA_RETRY_BACKOFF_MS', 300, source),
    topicPrefix: envString('KAFKA_TOPIC_PREFIX', 'rkgb', source),
    deadLetterSuffix: envString('KAFKA_DLQ_SUFFIX', '.dlq', source),
    retrySuffix: envString('KAFKA_RETRY_SUFFIX', '.retry', source),
  };
}

export interface TopicNameInput {
  domain: string;
  event: string;
  version?: number;
}

function topicPart(value: string): string {
  const normalized = value.trim().toLowerCase().replace(/[^a-z0-9._-]+/g, '-');
  if (!normalized) {
    throw new ConfigurationError('Kafka topic segments must not be empty');
  }
  return normalized;
}

export function buildTopicName(config: KafkaClientOptions, input: TopicNameInput): string {
  const version = input.version === undefined ? '' : `.v${input.version}`;
  return `${topicPart(config.topicPrefix)}.${topicPart(input.domain)}.${topicPart(input.event)}${version}`;
}

export function buildRetryTopicName(config: KafkaClientOptions, topic: string): string {
  return `${topicPart(topic)}${config.retrySuffix}`;
}

export function buildDeadLetterTopicName(config: KafkaClientOptions, topic: string): string {
  return `${topicPart(topic)}${config.deadLetterSuffix}`;
}

export interface KafkaMessage {
  key?: string;
  value: string;
  headers?: Record<string, string>;
}

export interface KafkaProducerLike {
  connect(): Promise<void>;
  send(input: {
    topic: string;
    messages: KafkaMessage[];
  }): Promise<void>;
  disconnect(): Promise<void>;
}

export interface KafkaConsumerLike {
  connect(): Promise<void>;
  subscribe(input: { topic: string; fromBeginning?: boolean }): Promise<void>;
  run(input: {
    eachMessage: (message: {
      topic: string;
      partition: number;
      message: { key?: Buffer | null; value?: Buffer | null; headers?: Record<string, Buffer | string | undefined> };
    }) => Promise<void>;
  }): Promise<void>;
  disconnect(): Promise<void>;
}

export interface KafkaFactory {
  producer(): KafkaProducerLike;
  consumer(groupId: string): KafkaConsumerLike;
}

class KafkaJsFactory implements KafkaFactory {
  constructor(private readonly client: Kafka) {}

  producer(): KafkaProducerLike {
    const producer: Producer = this.client.producer();
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

  consumer(groupId: string): KafkaConsumerLike {
    const consumer: Consumer = this.client.consumer({ groupId });
    return {
      connect: () => consumer.connect(),
      subscribe: (input) => consumer.subscribe(input),
      run: (input) =>
        consumer.run({
          eachMessage: async (payload) => {
            const headers: Record<string, string | undefined> = {};
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

export class KafkaConnection {
  private producerClient: KafkaProducerLike | undefined;
  private consumerClients = new Set<KafkaConsumerLike>();
  private connected = false;

  constructor(
    private readonly config: KafkaClientOptions,
    private readonly factory: KafkaFactory = new KafkaJsFactory(
      new Kafka({
        brokers: config.brokers,
        clientId: config.clientId,
        connectionTimeout: config.connectionTimeoutMs,
        requestTimeout: config.requestTimeoutMs,
        retry: {
          retries: config.retryAttempts,
          initialRetryTime: config.retryBackoffMs,
        },
      }),
    ),
  ) {}

  async connectProducer(): Promise<KafkaProducerLike> {
    if (!this.producerClient) {
      this.producerClient = this.factory.producer();
    }
    await this.producerClient.connect();
    this.connected = true;
    return this.producerClient;
  }

  async createConsumer(groupId = this.config.groupId): Promise<KafkaConsumerLike> {
    const consumer = this.factory.consumer(groupId);
    await consumer.connect();
    this.consumerClients.add(consumer);
    this.connected = true;
    return consumer;
  }

  async disconnect(): Promise<void> {
    const clients = [
      ...(this.producerClient ? [this.producerClient] : []),
      ...this.consumerClients,
    ];
    await Promise.all(clients.map((client) => client.disconnect()));
    this.consumerClients.clear();
    this.producerClient = undefined;
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }

  async health(): Promise<void> {
    if (!this.connected) {
      throw new Error('Kafka connection is not established');
    }
  }
}

export interface EventPublisher {
  publish<TData>(topic: string, event: EventEnvelope<TData>): Promise<void>;
}

export class KafkaEventPublisher implements EventPublisher {
  constructor(
    private readonly producer: KafkaProducerLike,
    private readonly connection: KafkaConnection,
  ) {}

  async publish<TData>(topic: string, event: EventEnvelope<TData>): Promise<void> {
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

export interface IdempotencyStore {
  has(key: string): Promise<boolean>;
  mark(key: string): Promise<void>;
}

export class InMemoryIdempotencyStore implements IdempotencyStore {
  private readonly processed = new Set<string>();

  async has(key: string): Promise<boolean> {
    return this.processed.has(key);
  }

  async mark(key: string): Promise<void> {
    this.processed.add(key);
  }
}

export interface EventConsumerOptions<TData> {
  topic: string;
  consumer: KafkaConsumerLike;
  idempotency: IdempotencyStore;
  handler: (event: EventEnvelope<TData>) => Promise<void>;
  publisher?: EventPublisher;
  config?: KafkaClientOptions;
  maxAttempts?: number;
}

export class KafkaEventConsumer<TData> {
  private running = false;

  constructor(private readonly options: EventConsumerOptions<TData>) {}

  async start(fromBeginning = false): Promise<void> {
    await this.options.consumer.subscribe({ topic: this.options.topic, fromBeginning });
    this.running = true;
    await this.options.consumer.run({
      eachMessage: async ({ message }) => {
        if (!message.value) {
          return;
        }
        const event = JSON.parse(message.value.toString()) as EventEnvelope<TData>;
        if (await this.options.idempotency.has(event.eventId)) {
          return;
        }
        try {
          await this.options.handler(event);
          await this.options.idempotency.mark(event.eventId);
        } catch (error) {
          await this.publishFailure(event, error);
          throw error;
        }
      },
    });
  }

  async stop(): Promise<void> {
    if (this.running) {
      await this.options.consumer.disconnect();
      this.running = false;
    }
  }

  isRunning(): boolean {
    return this.running;
  }

  private async publishFailure(event: EventEnvelope<TData>, error: unknown): Promise<void> {
    if (!this.options.publisher || !this.options.config) {
      return;
    }
    const attempts = this.options.maxAttempts ?? 3;
    const topic = buildDeadLetterTopicName(
      this.options.config,
      attempts > 0 ? this.options.topic : buildRetryTopicName(this.options.config, this.options.topic),
    );
    await this.options.publisher.publish(topic, {
      ...event,
      data: {
        originalEvent: event.data,
        failure: error instanceof Error ? error.message : 'Consumer handler failed',
      },
    });
  }
}

export interface KafkaHealth {
  connected: boolean;
  clientId: string;
  brokers: string[];
}

export function kafkaHealth(connection: KafkaConnection, config: KafkaClientOptions): KafkaHealth {
  return {
    connected: connection.isConnected(),
    clientId: config.clientId,
    brokers: config.brokers,
  };
}