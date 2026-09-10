import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { CorrelationIdMiddleware, createHealthController } from '@rkgb/common';
@Module({ controllers: [createHealthController('agent-worker-service')] })
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(CorrelationIdMiddleware).forRoutes('*');
  }
}
