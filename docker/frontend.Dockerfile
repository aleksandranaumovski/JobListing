FROM node:24-alpine AS build

WORKDIR /app
COPY frontend/package.json /app/package.json
RUN npm install
COPY frontend /app
RUN npm run build

FROM nginx:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/nvd-jobs/browser /usr/share/nginx/html
EXPOSE 80
