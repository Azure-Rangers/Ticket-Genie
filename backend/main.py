from api.tickets import router as ticket_router
from dotenv import load_dotenv
from fastapi import FastAPI
from telemetry import setup_telemetry

load_dotenv()

app = FastAPI(
    title="TicketGenie API",
    description="AI-powered HR & IT Helpdesk System",
    version="1.0",
)

# Initialize Azure Monitor telemetry
setup_telemetry(app)

app.include_router(ticket_router)


@app.get("/")
def root():
    return {"message": "Welcome to TicketGenie API!", "status": "Running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TicketGenie API"}
