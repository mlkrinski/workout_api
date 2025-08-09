@echo off
set PYTHONPATH=%CD%

if "%1"=="create-migrations" (
    alembic revision --autogenerate -m "%2"
    exit /b
)

if "%1"=="run-migrations" (
    alembic upgrade head
    exit /b
)

if "%1"=="run" (
    uvicorn workoutapi.main:app --reload
    exit /b
)

if "%1"=="docker" (
    docker-compose up -d
    exit /b
)

echo Comando não reconhecido. Use:
echo   run.bat create-migrations "mensagem"
echo   run.bat run-migrations
echo   run.bat run

