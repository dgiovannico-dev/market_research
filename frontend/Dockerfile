# Pin past Node2Shell (CVE-2026-111497); Node 20 is EOL / unpatched.
FROM node:22.23.4-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install
COPY . .

# Pre-create .next so anonymous volume init inherits non-root ownership (Compose).
RUN mkdir -p .next && chown -R node:node /app

USER node

EXPOSE 3000
# Exec-form next (not `npm run`) so closed stdin/TTY does not tear down the process.
CMD ["npx", "next", "dev", "-H", "0.0.0.0", "-p", "3000"]
