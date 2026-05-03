FROM ghcr.io/yalama34/coursearch/recsys-ml-base:latest

WORKDIR /app

COPY . .

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]