"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("./index");
const postgresConfig = {
    host: 'localhost',
    port: 5432,
    database: 'rkgb',
    user: 'rkgb',
    password: 'secret',
    ssl: false,
    maxConnections: 2,
};
class FakeSqlConnection {
    queries = [];
    async query(text) {
        this.queries.push(text);
        return { rows: [], rowCount: 0 };
    }
    release() { }
}
class FakeSqlPool {
    connection = new FakeSqlConnection();
    async connect() {
        return this.connection;
    }
    async query(text) {
        return this.connection.query(text);
    }
    async end() { }
}
class FakeRedis {
    status = 'ready';
    async connect() { }
    async ping() {
        return 'PONG';
    }
    async quit() {
        return 'OK';
    }
}
describe('database and storage foundations', () => {
    it('connects and probes PostgreSQL through an injectable pool', async () => {
        const client = new index_1.PostgresClient(postgresConfig, new FakeSqlPool());
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
        const runner = new index_1.MigrationRunner();
        const executed = await runner.run(connection, [
            {
                id: '001_documents',
                up: async (client) => {
                    await client.query('CREATE TABLE documents (id TEXT PRIMARY KEY)');
                },
            },
        ]);
        expect(executed).toEqual(['001_documents']);
        expect(connection.queries).toEqual(expect.arrayContaining(['BEGIN', 'COMMIT', 'CREATE TABLE documents (id TEXT PRIMARY KEY)']));
    });
    it('probes Neo4j through an injectable driver', async () => {
        const driver = {
            verifyConnectivity: jest.fn().mockResolvedValue(undefined),
            close: jest.fn().mockResolvedValue(undefined),
        };
        const config = {
            uri: 'bolt://localhost:7687',
            username: 'neo4j',
            password: 'secret',
            database: 'neo4j',
        };
        const client = new index_1.Neo4jClient(config, driver);
        await client.connect();
        await expect(client.health()).resolves.toMatchObject({ dependency: 'neo4j' });
        expect(driver.verifyConnectivity).toHaveBeenCalledTimes(2);
        await client.close();
    });
    it('probes Redis through an injectable client', async () => {
        const config = { url: 'redis://localhost:6379', keyPrefix: 'rkgb:' };
        const client = new index_1.RedisClient(config, new FakeRedis());
        await client.connect();
        await expect(client.health()).resolves.toMatchObject({ dependency: 'redis' });
        expect(client.isConnected()).toBe(true);
        await client.close();
    });
    it('bootstraps a MinIO bucket through an injectable client', async () => {
        const config = {
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
        const storage = new index_1.MinioObjectStorage(config, client);
        await storage.connect();
        expect(client.makeBucket).toHaveBeenCalledWith('rkgb-documents', 'us-east-1');
        await expect(storage.health()).resolves.toMatchObject({ dependency: 'minio' });
    });
});
//# sourceMappingURL=database.spec.js.map