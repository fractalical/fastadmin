from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, MetaData
import json
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory='templates')
SCHEMA_PATH = Path('schema.json')
db_engine = None

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    global db_engine
    if db_engine is None:
        return templates.TemplateResponse('index.html', {'request': request, 'connected': False})
    metadata = MetaData()
    metadata.reflect(bind=db_engine)
    tables = list(metadata.tables.keys())
    return templates.TemplateResponse('tables.html', {'request': request, 'tables': tables})

@app.post('/connect', response_class=HTMLResponse)
def connect(request: Request, db_url: str = Form(...)):
    global db_engine
    try:
        db_engine = create_engine(db_url)
        metadata = MetaData()
        metadata.reflect(bind=db_engine)
        tables = list(metadata.tables.keys())
        schemas = {t: [c.name for c in metadata.tables[t].columns] for t in tables}
        SCHEMA_PATH.write_text(json.dumps(schemas, indent=2))
        return templates.TemplateResponse('tables.html', {'request': request, 'tables': tables})
    except Exception as exc:
        db_engine = None
        return templates.TemplateResponse('index.html', {'request': request, 'connected': False, 'error': str(exc)})

@app.get('/table/{name}', response_class=HTMLResponse)
def show_table(name: str, request: Request):
    global db_engine
    if db_engine is None:
        raise HTTPException(status_code=400, detail='Not connected')
    metadata = MetaData()
    metadata.reflect(bind=db_engine)
    table = metadata.tables.get(name)
    if table is None:
        raise HTTPException(status_code=404, detail='Table not found')
    with db_engine.connect() as conn:
        rows = conn.execute(table.select().limit(100)).fetchall()
    tables = list(metadata.tables.keys())
    columns = [col.name for col in table.columns]
    return templates.TemplateResponse('table.html', {'request': request, 'table': name, 'rows': rows, 'columns': columns, 'tables': tables})
