FROM node:22-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

# Where nginx should proxy /api/* to — server-to-server, never seen by the
# browser. Fly: http://taskflow-nh-api.internal:8080 (private 6PN network).
# docker-compose: http://backend:8080 (compose service DNS).
ARG API_UPSTREAM=http://backend:8080

RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html

# Substituted at build time, then deliberately kept OUTSIDE
# /etc/nginx/templates/ — nginx:alpine's own entrypoint auto-runs envsubst
# on anything left in that directory *again* at container startup, and
# since API_UPSTREAM is a build ARG (not a runtime env var), that second
# pass leaves $API_UPSTREAM unresolved and crashes nginx on boot.
COPY nginx.conf.template /tmp/nginx.conf.template
RUN envsubst '$API_UPSTREAM' < /tmp/nginx.conf.template > /etc/nginx/conf.d/default.conf \
    && rm /tmp/nginx.conf.template

EXPOSE 8080
