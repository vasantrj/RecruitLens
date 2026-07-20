from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routers import jobs, candidates, matching, feedback, portfolio, integrations, outreach

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(candidates.router)
app.include_router(matching.router)
app.include_router(feedback.router)
app.include_router(portfolio.router)
app.include_router(integrations.router)
app.include_router(outreach.router)


@app.get("/")
def root():
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.get("/health")
def health_check():
    return {"status": "healthy"}