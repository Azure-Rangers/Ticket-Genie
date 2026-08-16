from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.admin import router as admin_router
from api.analytics import router as analytics_router
from api.announcements import router as announcements_router
from api.calendar import router as calendar_router
from api.chatbot import router as chatbot_router
from api.genie import router as genie_router
from api.knowledge import router as knowledge_router
from api.notifications import router as notifications_router
from api.onboarding import router as onboarding_router
from api.tickets import router as ticket_router
from api.users import router as users_router
from database.connection import init_db_schema
from database.seed import seed_initial_data
from telemetry import setup_telemetry

load_dotenv()

app = FastAPI(
    title="TicketGenie API",
    description="AI-powered HR & IT Helpdesk System",
    version="1.0",
)

# Initialize Database Schema & Seed Initial Data
init_db_schema()
seed_initial_data()

# Enable CORS for frontend dynamic requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Azure Monitor telemetry
setup_telemetry(app)

# Include API Routers under /api
app.include_router(ticket_router, prefix="/api")
app.include_router(genie_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(announcements_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(onboarding_router, prefix="/api")
app.include_router(users_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Welcome to TicketGenie API!", "status": "Running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TicketGenie API"}


@app.get("/api/config")
def get_public_config():
    import os

    return {
        "appInsightsConnectionString": os.getenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
        ),
        "azureClientId": os.getenv("AZURE_CLIENT_ID", ""),
        "azureTenantId": os.getenv("AZURE_TENANT_ID", ""),
    }
