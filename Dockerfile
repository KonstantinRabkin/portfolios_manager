FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
 && pip3 install --break-system-packages \
    fastapi uvicorn httpx openpyxl matplotlib python-multipart

WORKDIR /app

# Copy everything you need, not just root .py files
COPY . .

# (rest unchanged, e.g. command)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

