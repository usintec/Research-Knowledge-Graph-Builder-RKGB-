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
export declare function kafkaConfigFromEnv(source?: NodeJS.ProcessEnv, serviceName?: string): KafkaClientOptions;
export interface TopicNameInput {
    domain: string;
    event: string;
    version?: number;
}
export declare function buildTopicName(config: KafkaClientOptions, input: TopicNameInput): string;
export declare function buildRetryTopicName(config: KafkaClientOptions, topic: string): string;
export declare function buildDeadLetterTopicName(config: KafkaClientOptions, topic: string): string;
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
    subscribe(input: {
        topic: string;
        fromBeginning?: boolean;
    }): Promise<void>;
    run(input: {
        eachMessage: (message: {
            topic: string;
            partition: number;
            message: {
                key?: Buffer | null;
                value?: Buffer | null;
                headers?: Record<string, Buffer | string | undefined>;
            };
        }) => Promise<void>;
    }): Promise<void>;
    disconnect(): Promise<void>;
}
export interface KafkaFactory {
    producer(): KafkaProducerLike;
    consumer(groupId: string): KafkaConsumerLike;
}
export declare class KafkaConnection {
    private readonly config;
    private readonly factory;
    private producerClient;
    private consumerClients;
    private connected;
    constructor(config: KafkaClientOptions, factory?: KafkaFactory);
    connectProducer(): Promise<KafkaProducerLike>;
    createConsumer(groupId?: string): Promise<KafkaConsumerLike>;
    disconnect(): Promise<void>;
    isConnected(): boolean;
    health(): Promise<void>;
}
export interface EventPublisher {
    publish<TData>(topic: string, event: EventEnvelope<TData>): Promise<void>;
}
export declare class KafkaEventPublisher implements EventPublisher {
    private readonly producer;
    private readonly connection;
    constructor(producer: KafkaProducerLike, connection: KafkaConnection);
    publish<TData>(topic: string, event: EventEnvelope<TData>): Promise<void>;
}
export interface IdempotencyStore {
    has(key: string): Promise<boolean>;
    mark(key: string): Promise<void>;
}
export declare class InMemoryIdempotencyStore implements IdempotencyStore {
    private readonly processed;
    has(key: string): Promise<boolean>;
    mark(key: string): Promise<void>;
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
export declare class KafkaEventConsumer<TData> {
    private readonly options;
    private running;
    constructor(options: EventConsumerOptions<TData>);
    start(fromBeginning?: boolean): Promise<void>;
    stop(): Promise<void>;
    isRunning(): boolean;
    private publishFailure;
}
export interface KafkaHealth {
    connected: boolean;
    clientId: string;
    brokers: string[];
}
export declare function kafkaHealth(connection: KafkaConnection, config: KafkaClientOptions): KafkaHealth;
//# sourceMappingURL=index.d.ts.map