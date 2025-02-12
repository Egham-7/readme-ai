FROM oven/bun:latest AS build

WORKDIR /app

COPY package.json bun.lockb ./

RUN bun install --frozen-lockfile

COPY . .

ARG VITE_BASE_API_URL
ARG VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_BASE_API_URL=$VITE_BASE_API_URL
ENV VITE_CLERK_PUBLISHABLE_KEY=${VITE_CLERK_PUBLISHABLE_KEY}

RUN bun run build

FROM caddy:latest

WORKDIR /app

COPY Caddyfile ./

RUN caddy fmt Caddyfile --overwrite

COPY --from=build /app/dist ./dist

EXPOSE 80

CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]

