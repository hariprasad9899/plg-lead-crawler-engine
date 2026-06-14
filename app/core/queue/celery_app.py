from celery import Celery

celery_app = Celery(
    "plg_lead_crawler",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

import app.search_worker.task
