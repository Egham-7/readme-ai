# Use the official Bun image
FROM oven/bun:1 AS build

# Set workdir
WORKDIR /app

# Copy package files first to leverage caching
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source files
COPY . .

# Build the application
RUN bun run build

# Use Caddy as the production image
FROM caddy:2-alpine

WORKDIR /app

# Copy and format Caddyfile
COPY Caddyfile ./
RUN caddy fmt Caddyfile --overwrite

# Copy built assets from build stage
COPY --from=build /app/dist ./dist

# Expose port 80
EXPOSE 80

# Use non-root user for better security
USER caddy

# Run Caddy
CMD ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]

