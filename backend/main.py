from api.tickets import router as ticket_router
from fastapi import FastAPI

app = FastAPI(
    title="TicketGenie API",
    description="AI-powered HR & IT Helpdesk System",
    version="1.0",
)

app.include_router(ticket_router)


@app.get("/")
def root():
    return {"message": "Welcome to TicketGenie API!", "status": "Running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "TicketGenie API"}
