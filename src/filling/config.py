import os


def get_postgres_uri() -> str:
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "Qwe123")
    user, db_name = "timesheet", "timesheet"
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"
