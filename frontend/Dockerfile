# ---- Build the static bundle ----
FROM node:22-alpine AS build

WORKDIR /app

# Copy manifests first: this layer is cached unless dependencies change,
# so editing source does not trigger a reinstall.
COPY package*.json ./
RUN npm ci

COPY . .

# Vite inlines env vars at BUILD time, not runtime — so the API URL must be
# supplied here, not in docker-compose's `environment:`.
ARG VITE_API_BASE_URL=http://localhost:8001/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# ---- Serve it ----
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
