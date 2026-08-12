from api.genie import router as genie_router
from api.tickets import router as ticket_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from telemetry import setup_telemetry

load_dotenv()

app = FastAPI(
    title="TicketGenie API",
    description="AI-powered HR & IT Helpdesk System",
    version="1.0",
)

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


@app.get("/")
def root():
    return {"message": "Welcome to TicketGenie API!", "status": "Running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TicketGenie API"}
