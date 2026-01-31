docker stop stock-app || true
docker rm stock-app || true

docker build -t stock-table:latest .

docker run -d \
  --name stock-app \
  -p 8080:8000 \
  -v /srv/stock-table-backups:/app/backups \
  stock-table:latest

