from fastapi import FastAPI
from routers.backup import router as backup_router
from routers.ui import router as ui_router
from routers.portfolio import router as portfolio_router
from routers.tickers import router as tickers_router
from routers.import_export import router as import_export_router
from routers.charts import router as charts_router
from backup_utils import load_latest_backup_on_startup
from routers.config import router as config_router

app = FastAPI()

app.include_router(backup_router)
app.include_router(ui_router)
app.include_router(portfolio_router)
app.include_router(tickers_router)
app.include_router(import_export_router)
app.include_router(charts_router)
app.include_router(config_router)

@app.on_event("startup")
def startup_load_backup():
    load_latest_backup_on_startup()

