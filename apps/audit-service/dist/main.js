"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
require("reflect-metadata");
const core_1 = require("@nestjs/core");
const common_1 = require("@rkgb/common");
const app_module_1 = require("./app.module");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule, {
        logger: new common_1.StructuredLogger('audit-service'),
    });
    app.useGlobalFilters(new common_1.CommonHttpExceptionFilter());
    app.enableShutdownHooks();
    await app.listen(Number(process.env.PORT ?? 3000));
}
void bootstrap();
//# sourceMappingURL=main.js.map