# Build context: repository root.  (Northflank: Dockerfile path /apps/server/Dockerfile, context /)
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production

COPY package.json package-lock.json ./
COPY packages/shared/package.json packages/shared/
COPY apps/server/package.json apps/server/
RUN npm ci --omit=dev -w @wisp/server -w @wisp/shared --include-workspace-root=false

COPY packages/shared packages/shared
COPY apps/server/src apps/server/src

USER node
EXPOSE 8080
CMD ["node", "apps/server/src/index.js"]
