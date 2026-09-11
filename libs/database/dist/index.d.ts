import { type Driver } from 'neo4j-driver';
import { Client as MinioClient } from 'minio';
import { type QueryResultRow } from 'pg';
import type { RedisLike } from './redis.types';
export type { RedisLike } from './redis.types';
export interface PostgresConfig {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
    ssl: boolean;
    maxConnections: number;
}
export interface Neo4jConfig {
    uri: string;
    username: string;
    password: string;
    database: string;
}
export interface RedisConfig {
    url: string;
    keyPrefix: string;
}
export interface MinioConfig {
    endpoint: string;
    port: number;
    useSSL: boolean;
    accessKey: string;
    secretKey: string;
    bucket: string;
    region: string;
}
export interface InfrastructureDatabaseConfig {
    postgres: PostgresConfig;
    neo4j: Neo4jConfig;
    redis: RedisConfig;
    minio: MinioConfig;
}
export declare function infrastructureConfigFromEnv(source?: NodeJS.ProcessEnv): InfrastructureDatabaseConfig;
export interface DatabaseHealth {
    connected: boolean;
    dependency: string;
    details?: Record<string, string | number | boolean>;
}
export interface SqlResult<T extends QueryResultRow = QueryResultRow> {
    rows: T[];
    rowCount: number | null;
}
export interface SqlConnection {
    query<T extends QueryResultRow = QueryResultRow>(text: string, values?: readonly unknown[]): Promise<SqlResult<T>>;
    release(): void;
}
export interface SqlPool {
    connect(): Promise<SqlConnection>;
    query<T extends QueryResultRow = QueryResultRow>(text: string, values?: readonly unknown[]): Promise<SqlResult<T>>;
    end(): Promise<void>;
}
export declare class PostgresClient {
    private readonly config;
    private readonly pool;
    private connected;
    constructor(config: PostgresConfig, pool?: SqlPool);
    connect(): Promise<void>;
    query<T extends QueryResultRow = QueryResultRow>(text: string, values?: readonly unknown[]): Promise<SqlResult<T>>;
    health(): Promise<DatabaseHealth>;
    close(): Promise<void>;
    isConnected(): boolean;
}
export interface Migration {
    id: string;
    up(client: SqlConnection): Promise<void>;
}
export declare class MigrationRunner {
    run(client: SqlConnection, migrations: readonly Migration[]): Promise<string[]>;
}
export declare class Neo4jClient {
    private readonly config;
    private readonly driver;
    private connected;
    constructor(config: Neo4jConfig, driver?: Pick<Driver, 'verifyConnectivity' | 'close'>);
    connect(): Promise<void>;
    health(): Promise<DatabaseHealth>;
    close(): Promise<void>;
    isConnected(): boolean;
}
export declare class RedisClient {
    private readonly config;
    private readonly client;
    private connected;
    constructor(config: RedisConfig, client?: RedisLike);
    connect(): Promise<void>;
    health(): Promise<DatabaseHealth>;
    close(): Promise<void>;
    isConnected(): boolean;
}
export declare class MinioObjectStorage {
    private readonly config;
    private readonly client;
    private connected;
    constructor(config: MinioConfig, client?: Pick<MinioClient, 'bucketExists' | 'makeBucket'>);
    connect(): Promise<void>;
    ensureBucket(): Promise<void>;
    health(): Promise<DatabaseHealth>;
    isConnected(): boolean;
}
//# sourceMappingURL=index.d.ts.map