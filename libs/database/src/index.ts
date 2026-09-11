import { envBoolean, envNumber, envString, ConfigurationError } from '@rkgb/common';
import neo4j, { type Driver } from 'neo4j-driver';
import Redis from 'ioredis';
import { Client as MinioClient } from 'minio';
import { Pool, type QueryResultRow } from 'pg';
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

export function infrastructureConfigFromEnv(
  source: NodeJS.ProcessEnv = process.env,
): InfrastructureDatabaseConfig {
  const postgres: PostgresConfig = {
    host: envString('POSTGRES_HOST', 'localhost', source),
    port: envNumber('POSTGRES_PORT', 5432, source),
    database: envString('POSTGRES_DB', 'rkgb', source),
    user: envString('POSTGRES_USER', 'rkgb', source),
    password: envString('POSTGRES_PASSWORD', 'rkgb_dev_password', source),
    ssl: envBoolean('POSTGRES_SSL', false, source),
    maxConnections: envNumber('POSTGRES_POOL_MAX', 10, source),
  };
  const neo4jConfig: Neo4jConfig = {
    uri: envString('NEO4J_URI', 'bolt://localhost:7687', source),
    username: envString('NEO4J_USERNAME', 'neo4j', source),
    password: envString('NEO4J_PASSWORD', 'rkgb_dev_password', source),
    database: envString('NEO4J_DATABASE', 'neo4j', source),
  };
  const redis: RedisConfig = {
    url: envString('REDIS_URL', 'redis://localhost:6379', source),
    keyPrefix: envString('REDIS_KEY_PREFIX', 'rkgb:', source),
  };
  const minio: MinioConfig = {
    endpoint: envString('MINIO_ENDPOINT', 'localhost', source),
    port: envNumber('MINIO_PORT', 9000, source),
    useSSL: envBoolean('MINIO_USE_SSL', false, source),
    accessKey: envString('MINIO_ROOT_USER', 'rkgb_minio', source),
    secretKey: envString('MINIO_ROOT_PASSWORD', 'rkgb_minio_password', source),
    bucket: envString('MINIO_BUCKET', 'rkgb-documents', source),
    region: envString('MINIO_REGION', 'us-east-1', source),
  };
  if (!/^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$/.test(minio.bucket)) {
    throw new ConfigurationError('MINIO_BUCKET must be a valid bucket name');
  }
  return { postgres, neo4j: neo4jConfig, redis, minio };
}

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
  query<T extends QueryResultRow = QueryResultRow>(
    text: string,
    values?: readonly unknown[],
  ): Promise<SqlResult<T>>;
  release(): void;
}

export interface SqlPool {
  connect(): Promise<SqlConnection>;
  query<T extends QueryResultRow = QueryResultRow>(
    text: string,
    values?: readonly unknown[],
  ): Promise<SqlResult<T>>;
  end(): Promise<void>;
}

export class PostgresClient {
  private connected = false;

  constructor(
    private readonly config: PostgresConfig,
    private readonly pool: SqlPool = new Pool({
      host: config.host,
      port: config.port,
      database: config.database,
      user: config.user,
      password: config.password,
      max: config.maxConnections,
      ssl: config.ssl ? { rejectUnauthorized: false } : false,
    }),
  ) {}

  async connect(): Promise<void> {
    const client = await this.pool.connect();
    client.release();
    this.connected = true;
  }

  async query<T extends QueryResultRow = QueryResultRow>(
    text: string,
    values?: readonly unknown[],
  ): Promise<SqlResult<T>> {
    return this.pool.query<T>(text, values);
  }

  async health(): Promise<DatabaseHealth> {
    await this.query('SELECT 1');
    return {
      connected: true,
      dependency: 'postgres',
      details: { host: this.config.host, database: this.config.database },
    };
  }

  async close(): Promise<void> {
    await this.pool.end();
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}

export interface Migration {
  id: string;
  up(client: SqlConnection): Promise<void>;
}

export class MigrationRunner {
  async run(client: SqlConnection, migrations: readonly Migration[]): Promise<string[]> {
    await client.query(`
      CREATE TABLE IF NOT EXISTS rkgb_schema_migrations (
        id TEXT PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
    const appliedResult = await client.query<{ id: string }>(
      'SELECT id FROM rkgb_schema_migrations ORDER BY id',
    );
    const applied = new Set(appliedResult.rows.map((row) => row.id));
    const executed: string[] = [];
    for (const migration of migrations) {
      if (applied.has(migration.id)) {
        continue;
      }
      await client.query('BEGIN');
      try {
        await migration.up(client);
        await client.query('INSERT INTO rkgb_schema_migrations (id) VALUES ($1)', [migration.id]);
        await client.query('COMMIT');
        executed.push(migration.id);
      } catch (error) {
        await client.query('ROLLBACK');
        throw error;
      }
    }
    return executed;
  }
}

export class Neo4jClient {
  private connected = false;

  constructor(
    private readonly config: Neo4jConfig,
    private readonly driver: Pick<Driver, 'verifyConnectivity' | 'close'> = neo4j.driver(
      config.uri,
      neo4j.auth.basic(config.username, config.password),
    ),
  ) {}

  async connect(): Promise<void> {
    await this.driver.verifyConnectivity();
    this.connected = true;
  }

  async health(): Promise<DatabaseHealth> {
    await this.driver.verifyConnectivity();
    return {
      connected: true,
      dependency: 'neo4j',
      details: { uri: this.config.uri, database: this.config.database },
    };
  }

  async close(): Promise<void> {
    await this.driver.close();
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}

export class RedisClient {
  private connected = false;

  constructor(
    private readonly config: RedisConfig,
    private readonly client: RedisLike = new Redis(config.url, {
      keyPrefix: config.keyPrefix,
      lazyConnect: true,
    }),
  ) {}

  async connect(): Promise<void> {
    if (this.client.status === 'wait') {
      await this.client.connect();
    }
    await this.client.ping();
    this.connected = true;
  }

  async health(): Promise<DatabaseHealth> {
    await this.client.ping();
    return { connected: true, dependency: 'redis' };
  }

  async close(): Promise<void> {
    await this.client.quit();
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}

export class MinioObjectStorage {
  private connected = false;

  constructor(
    private readonly config: MinioConfig,
    private readonly client: Pick<MinioClient, 'bucketExists' | 'makeBucket'> = new MinioClient({
      endPoint: config.endpoint,
      port: config.port,
      useSSL: config.useSSL,
      accessKey: config.accessKey,
      secretKey: config.secretKey,
      region: config.region,
    }),
  ) {}

  async connect(): Promise<void> {
    await this.ensureBucket();
    this.connected = true;
  }

  async ensureBucket(): Promise<void> {
    const exists = await this.client.bucketExists(this.config.bucket);
    if (!exists) {
      await this.client.makeBucket(this.config.bucket, this.config.region);
    }
  }

  async health(): Promise<DatabaseHealth> {
    await this.ensureBucket();
    return {
      connected: true,
      dependency: 'minio',
      details: { bucket: this.config.bucket, endpoint: this.config.endpoint },
    };
  }

  isConnected(): boolean {
    return this.connected;
  }
}