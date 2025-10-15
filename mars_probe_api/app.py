from fastapi import FastAPI 

from mars_probe_api.routers import probes

app = FastAPI()
app.include_router(probes.router)
