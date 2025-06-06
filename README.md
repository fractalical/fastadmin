# FastAdmin

Simple FastAPI app to browse tables from any PostgreSQL database.

## Usage

1. Edit `docker-compose.yml` or set the database URL when connecting.
2. Run the application:

```bash
docker compose up --build
```

3. Open `http://localhost:8000` in your browser and enter the PostgreSQL connection URL. Example:

```
postgresql://user:password@hostname:5432/dbname
```

The app will read all tables, save their schemas to `schema.json` and display the table list. Select a table from the sidebar to view its contents.
