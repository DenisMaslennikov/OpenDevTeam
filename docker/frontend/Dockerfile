FROM node:24-alpine

WORKDIR /app

COPY packages/frontend/.npmrc packages/frontend/package.json packages/frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY packages/frontend/ ./

ENV HOST=0.0.0.0
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
