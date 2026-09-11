import {
  MigrationRunner,
  MinioObjectStorage,
  Neo4jClient,
  PostgresClient,
  RedisClient,
  type MinioConfig,
  type Neo4jConfig,
  type PostgresConfig,
  type RedisConfig,
  type RedisLike,
  type SqlConnection,
  type SqlPool,
} from './index';

const postgresConfig: PostgresConfig = {
  host: 'localhost',
  port: 5432,
  database: 'rkgb',
  user: 'rkgb',
  password: 'secret',
  ssl: false,
  maxConnections: 2,
};

class FakeSqlConnection implements SqlConnection {
  readonly queries: string[] = [];

  async query<T extends object = Record<string, unknown>>(
    text: string,
  ): Promise<{ rows: T[]; rowCount: number }> {
    this.queries.push(text);
    return { rows: [] as T[], rowCount: 0 };
  }

  release(): void {}
}

class FakeSqlPool implements SqlPool {
  readonly connection = new FakeSqlConnection();

  async connect(): Promise<SqlConnection> {
    return this.connection;
  }

  async query<T extends object = Record<string, unknown>>(
    text: string,
  ): Promise<{ rows: T[]; rowCount: number }> {
    return this.connection.query<T>(text);
  }

  async end(): Promise<void> {}
}

class FakeRedis implements RedisLike {
  readonly status = 'ready';

  async connect(): Promise<void> {}

  async ping(): Promise<string> {
    return 'PONG';
  }

  async quit(): Promise<string> {
    return 'OK';
  }
}

describe('database and storage foundations', () => {
  it('connects and probes PostgreSQL through an injectable pool', async () => {
    const client = new PostgresClient(postgresConfig, new FakeSqlPool());
    await client.connect();
    expect(client.isConnected()).toBe(true);
    await expect(client.health()).resolves.toMatchObject({
      dependency: 'postgres',
      connected: true,
    });
    await client.close();
  });

  it('runs only unapplied migrations transactionally', async () => {
    const connection = new FakeSqlConnection();
    const runner = new MigrationRunner();
    const executed = await runner.run(connection, [
      {
        id: '001_documents',
        up: async (client) => {
          await client.query('CREATE TABLE documents (id TEXT PRIMARY KEY)');
        },
      },
    ]);
    expect(executed).toEqual(['001_documents']);
    expect(connection.queries).toEqual(
      expect.arrayContaining(['BEGIN', 'COMMIT', 'CREATE TABLE documents (id TEXT PRIMARY KEY)']),
    );
  });

  it('probes Neo4j through an injectable driver', async () => {
    const driver = {
      verifyConnectivity: jest.fn().mockResolvedValue(undefined),
      close: jest.fn().mockResolvedValue(undefined),
    };
    const config: Neo4jConfig = {
      uri: 'bolt://localhost:7687',
      username: 'neo4j',
      password: 'secret',
      database: 'neo4j',
    };
    const client = new Neo4jClient(config, driver);
    await client.connect();
    await expect(client.health()).resolves.toMatchObject({ dependency: 'neo4j' });
    expect(driver.verifyConnectivity).toHaveBeenCalledTimes(2);
    await client.close();
  });

  it('probes Redis through an injectable client', async () => {
    const config: RedisConfig = { url: 'redis://localhost:6379', keyPrefix: 'rkgb:' };
    const client = new RedisClient(config, new FakeRedis());
    await client.connect();
    await expect(client.health()).resolves.toMatchObject({ dependency: 'redis' });
    expect(client.isConnected()).toBe(true);
    await client.close();
  });

  it('bootstraps a MinIO bucket through an injectable client', async () => {
    const config: MinioConfig = {
      endpoint: 'localhost',
      port: 9000,
      useSSL: false,
      accessKey: 'access',
      secretKey: 'secret',
      bucket: 'rkgb-documents',
      region: 'us-east-1',
    };
    const client = {
      bucketExists: jest.fn().mockResolvedValue(false),
      makeBucket: jest.fn().mockResolvedValue(undefined),
    };
    const storage = new MinioObjectStorage(config, client);
    await storage.connect();
    expect(client.makeBucket).toHaveBeenCalledWith('rkgb-documents', 'us-east-1');
    await expect(storage.health()).resolves.toMatchObject({ dependency: 'minio' });
  });
});