FROM python:3.11-slim
RUN apt-get update && apt-get install -y
COPY .devcontainer/requirements.txt .
RUN pip install -r --no-cache-dir requirements.txt 
COPY . . 
EXPOSE 8000 
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retires=3 \
    CMD curl -f http://localhost:8000/health || exit 1 
CMD ["python", "-m", "app.main"] 