# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-retries 5 && \
    npm install --retry=3
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node
ENV PORT=8000
EXPOSE 8000
CMD ["node", "dist/index.js"]
