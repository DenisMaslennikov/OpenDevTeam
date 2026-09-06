FROM ghcr.io/berriai/litellm:main-latest

WORKDIR /app

COPY docker/litellm/litellm-config.yaml /app/config.yaml

ENV LITELLM_PORT=4000
EXPOSE 4000

CMD ["--config", "/app/config.yaml", "--port", "4000"]
