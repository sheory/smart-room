sudo apt update && sudo apt install libpq-dev
docker-compose down -v
docker-compose up -d
docker exec -it postgres_db bash
alembic revision --autogenerate -m "Descrição da sua migração"

apos subir o docker:
    alembic upgrade head
alembic downgrade -1

http://localhost:8000/docs