export interface RedisLike {
    readonly status: string;
    connect(): Promise<void>;
    ping(): Promise<string>;
    quit(): Promise<string>;
}
//# sourceMappingURL=redis.types.d.ts.map