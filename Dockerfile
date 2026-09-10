FROM node:20-bookworm-slim AS build
WORKDIR /workspace
RUN corepack enable
COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
COPY apps ./apps
COPY libs ./libs
COPY tsconfig.base.json ./
RUN pnpm install --frozen-lockfile=false
ARG APP
RUN pnpm --filter "@rkgb/${APP}" build

FROM node:20-bookworm-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN corepack enable
ARG APP
COPY --from=build /workspace/apps/${APP}/dist ./dist
COPY --from=build /workspace/node_modules ./node_modules
COPY --from=build /workspace/apps/${APP}/package.json ./
EXPOSE 3000
CMD ["node", "dist/main.js"]