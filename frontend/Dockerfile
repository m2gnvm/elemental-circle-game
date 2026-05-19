# ── Stage 1: Build Flutter web ────────────────────────────────────────────────
FROM ghcr.io/cirruslabs/flutter:stable AS builder

WORKDIR /app

# Copy dependency manifests first for better layer caching
COPY pubspec.yaml pubspec.lock* ./
RUN flutter pub get

# Copy the rest of the source
COPY . .

# Build args let docker-compose (or CI) override the backend URLs at build time
ARG BASE_URL=http://localhost:8000
ARG WS_BASE_URL=ws://localhost:8000

RUN flutter build web --release \
    --dart-define=BASE_URL=${BASE_URL} \
    --dart-define=WS_BASE_URL=${WS_BASE_URL}

# ── Stage 2: Serve with Nginx ──────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Copy the Flutter web build output
COPY --from=builder /app/build/web /usr/share/nginx/html

# Copy our Nginx config (SPA routing + API/WS proxy)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
