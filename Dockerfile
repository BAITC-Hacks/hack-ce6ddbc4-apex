FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /srv/tandau

COPY requirements.txt requirements-llm.txt ./
ARG WITH_LLM=0
RUN pip install --no-cache-dir -r requirements.txt \
 && if [ "$WITH_LLM" = "1" ]; then pip install --no-cache-dir -r requirements-llm.txt; fi

COPY . .

EXPOSE 8000
CMD ["python", "run.py"]
