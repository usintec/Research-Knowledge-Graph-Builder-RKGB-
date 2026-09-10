import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { CommonHttpExceptionFilter, StructuredLogger } from '@rkgb/common';
import { AppModule } from './app.module';
async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule, {
    logger: new StructuredLogger('knowledge-extraction-service'),
  });
  app.useGlobalFilters(new CommonHttpExceptionFilter());
  app.enableShutdownHooks();
  await app.listen(Number(process.env.PORT ?? 3000));
}
void bootstrap();
