FROM oven/bun:1 AS build

WORKDIR /app

COPY package.json bun.lockb ./

RUN bun install --frozen-lockfile

COPY . .

ARG VITE_BASE_API_URL
ENV VITE_BASE_API_URL=$VITE_BASE_API_URL

RUN bun run build

FROM caddy:latest

WORKDIR /app

COPY Caddyfile ./

RUN caddy fmt Caddyfile --overwrite

COPY --from=build /app/dist ./dist

EXPOSE 80

CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]

