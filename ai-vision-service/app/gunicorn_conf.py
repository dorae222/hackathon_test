import multiprocessing
import os

bind = "0.0.0.0:8000"

_default_workers = 1 + multiprocessing.cpu_count() // 2

def getenv_int(name: str, default: int) -> int:
	val = os.getenv(name)
	if val is None or val.strip() == "":
		return default
	try:
		return int(val)
	except ValueError:
		return default

workers = getenv_int("GUNICORN_WORKERS", min(2, _default_workers))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
