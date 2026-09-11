"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MinioObjectStorage = exports.RedisClient = exports.Neo4jClient = exports.MigrationRunner = exports.PostgresClient = void 0;
exports.infrastructureConfigFromEnv = infrastructureConfigFromEnv;
const common_1 = require("@rkgb/common");
const neo4j_driver_1 = __importDefault(require("neo4j-driver"));
const ioredis_1 = __importDefault(require("ioredis"));
const minio_1 = require("minio");
const pg_1 = require("pg");
function infrastructureConfigFromEnv(source = process.env) {
    const postgres = {
        host: (0, common_1.envString)('POSTGRES_HOST', 'localhost', source),
        port: (0, common_1.envNumber)('POSTGRES_PORT', 5432, source),
        database: (0, common_1.envString)('POSTGRES_DB', 'rkgb', source),
        user: (0, common_1.envString)('POSTGRES_USER', 'rkgb', source),
        password: (0, common_1.envString)('POSTGRES_PASSWORD', 'rkgb_dev_password', source),
        ssl: (0, common_1.envBoolean)('POSTGRES_SSL', false, source),
        maxConnections: (0, common_1.envNumber)('POSTGRES_POOL_MAX', 10, source),
    };
    const neo4jConfig = {
        uri: (0, common_1.envString)('NEO4J_URI', 'bolt://localhost:7687', source),
        username: (0, common_1.envString)('NEO4J_USERNAME', 'neo4j', source),
        password: (0, common_1.envString)('NEO4J_PASSWORD', 'rkgb_dev_password', source),
        database: (0, common_1.envString)('NEO4J_DATABASE', 'neo4j', source),
    };
    const redis = {
        url: (0, common_1.envString)('REDIS_URL', 'redis://localhost:6379', source),
        keyPrefix: (0, common_1.envString)('REDIS_KEY_PREFIX', 'rkgb:', source),
    };
    const minio = {
        endpoint: (0, common_1.envString)('MINIO_ENDPOINT', 'localhost', source),
        port: (0, common_1.envNumber)('MINIO_PORT', 9000, source),
        useSSL: (0, common_1.envBoolean)('MINIO_USE_SSL', false, source),
        accessKey: (0, common_1.envString)('MINIO_ROOT_USER', 'rkgb_minio', source),
        secretKey: (0, common_1.envString)('MINIO_ROOT_PASSWORD', 'rkgb_minio_password', source),
        bucket: (0, common_1.envString)('MINIO_BUCKET', 'rkgb-documents', source),
        region: (0, common_1.envString)('MINIO_REGION', 'us-east-1', source),
    };
    if (!/^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$/.test(minio.bucket)) {
        throw new common_1.ConfigurationError('MINIO_BUCKET must be a valid bucket name');
    }
    return { postgres, neo4j: neo4jConfig, redis, minio };
}
class PostgresClient {
    config;
    pool;
    connected = false;
    constructor(config, pool = new pg_1.Pool({
        host: config.host,
        port: config.port,
        database: config.database,
        user: config.user,
        password: config.password,
        max: config.maxConnections,
        ssl: config.ssl ? { rejectUnauthorized: false } : false,
    })) {
        this.config = config;
        this.pool = pool;
    }
    async connect() {
        const client = await this.pool.connect();
        client.release();
        this.connected = true;
    }
    async query(text, values) {
        return this.pool.query(text, values);
    }
    async health() {
        await this.query('SELECT 1');
        return {
            connected: true,
            dependency: 'postgres',
            details: { host: this.config.host, database: this.config.database },
        };
    }
    async close() {
        await this.pool.end();
        this.connected = false;
    }
    isConnected() {
        return this.connected;
    }
}
exports.PostgresClient = PostgresClient;
class MigrationRunner {
    async run(client, migrations) {
        await client.query(`
      CREATE TABLE IF NOT EXISTS rkgb_schema_migrations (
        id TEXT PRIMARY KEY,
        applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
        const appliedResult = await client.query('SELECT id FROM rkgb_schema_migrations ORDER BY id');
        const applied = new Set(appliedResult.rows.map((row) => row.id));
        const executed = [];
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
            }
            catch (error) {
                await client.query('ROLLBACK');
                throw error;
            }
        }
        return executed;
    }
}
exports.MigrationRunner = MigrationRunner;
class Neo4jClient {
    config;
    driver;
    connected = false;
    constructor(config, driver = neo4j_driver_1.default.driver(config.uri, neo4j_driver_1.default.auth.basic(config.username, config.password))) {
        this.config = config;
        this.driver = driver;
    }
    async connect() {
        await this.driver.verifyConnectivity();
        this.connected = true;
    }
    async health() {
        await this.driver.verifyConnectivity();
        return {
            connected: true,
            dependency: 'neo4j',
            details: { uri: this.config.uri, database: this.config.database },
        };
    }
    async close() {
        await this.driver.close();
        this.connected = false;
    }
    isConnected() {
        return this.connected;
    }
}
exports.Neo4jClient = Neo4jClient;
class RedisClient {
    config;
    client;
    connected = false;
    constructor(config, client = new ioredis_1.default(config.url, {
        keyPrefix: config.keyPrefix,
        lazyConnect: true,
    })) {
        this.config = config;
        this.client = client;
    }
    async connect() {
        if (this.client.status === 'wait') {
            await this.client.connect();
        }
        await this.client.ping();
        this.connected = true;
    }
    async health() {
        await this.client.ping();
        return { connected: true, dependency: 'redis' };
    }
    async close() {
        await this.client.quit();
        this.connected = false;
    }
    isConnected() {
        return this.connected;
    }
}
exports.RedisClient = RedisClient;
class MinioObjectStorage {
    config;
    client;
    connected = false;
    constructor(config, client = new minio_1.Client({
        endPoint: config.endpoint,
        port: config.port,
        useSSL: config.useSSL,
        accessKey: config.accessKey,
        secretKey: config.secretKey,
        region: config.region,
    })) {
        this.config = config;
        this.client = client;
    }
    async connect() {
        await this.ensureBucket();
        this.connected = true;
    }
    async ensureBucket() {
        const exists = await this.client.bucketExists(this.config.bucket);
        if (!exists) {
            await this.client.makeBucket(this.config.bucket, this.config.region);
        }
    }
    async health() {
        await this.ensureBucket();
        return {
            connected: true,
            dependency: 'minio',
            details: { bucket: this.config.bucket, endpoint: this.config.endpoint },
        };
    }
    isConnected() {
        return this.connected;
    }
}
exports.MinioObjectStorage = MinioObjectStorage;
//# sourceMappingURL=index.js.map