from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import os
from pathlib import Path

from app.database.connection import get_db, engine
from app.models.database import Base
from app.routers import leads
from app.schemas.lead_schema import LeadCreate
from app.models.database import Lead

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Consultancy Services",
    description="Professional AI Chatbot Integration Services",
    version="1.0.0"
)

# Mount static files - Make sure this path is correct
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Debug: Print paths to verify
print(f"BASE_DIR: {BASE_DIR}")
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"TEMPLATES_DIR: {TEMPLATES_DIR}")
print(f"Static directory exists: {STATIC_DIR.exists()}")
print(f"Templates directory exists: {TEMPLATES_DIR.exists()}")

# Check CSS file specifically
css_file = STATIC_DIR / "css" / "style.css"
print(f"CSS file path: {css_file}")
print(f"CSS file exists: {css_file.exists()}")

# List contents of static directory if it exists
if STATIC_DIR.exists():
    print(f"Contents of static directory: {list(STATIC_DIR.iterdir())}")
    css_dir = STATIC_DIR / "css"
    if css_dir.exists():
        print(f"Contents of css directory: {list(css_dir.iterdir())}")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print("✅ Static files mounted successfully")
except Exception as e:
    print(f"❌ Error mounting static files: {e}")

def load_template(template_name: str, context: dict = None) -> str:
    """Load HTML template and inject CSS if needed"""
    template_path = TEMPLATES_DIR / template_name
    
    print(f"Looking for template at: {template_path}")
    
    if not template_path.exists():
        if TEMPLATES_DIR.exists():
            available_files = list(TEMPLATES_DIR.glob("*"))
            print(f"Available files in templates directory: {available_files}")
        raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Enhanced CSS injection - Add CSS in head section
    css_links = [
        '<link rel="stylesheet" href="/static/css/style.css">',
        '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">',
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">'
    ]
    
    # Check if CSS is already included
    if '/static/css/style.css' not in content:
        if '<head>' in content:
            css_block = '\n    '.join(css_links)
            content = content.replace('<head>', f'<head>\n    {css_block}')
        else:
            # If no head tag, add it
            css_block = '\n'.join(css_links)
            head_section = f'<head>\n{css_block}\n</head>'
            if '<html>' in content:
                content = content.replace('<html>', f'<html>\n{head_section}')
            else:
                content = f'<!DOCTYPE html>\n<html>\n{head_section}\n<body>\n{content}\n</body>\n</html>'
    
    print(f"✅ CSS injection check completed for {template_name}")
    
    # Simple placeholder replacement
    if context:
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
    
    return content

# Include routers
app.include_router(leads.router, prefix="/api", tags=["leads"])

# Routes
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Serve the homepage with CSS"""
    try:
        html_content = load_template("index.html")
        return HTMLResponse(content=html_content)
    except FileNotFoundError as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=404)

@app.get("/contact", response_class=HTMLResponse)
async def contact_form(request: Request):
    """Serve the contact form with CSS"""
    try:
        html_content = load_template("form.html")
        return HTMLResponse(content=html_content)
    except FileNotFoundError as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=404)

@app.post("/submit-lead")
async def submit_lead(
    request: Request,
    company_name: str = Form(...),
    contact_person: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    profession: str = Form(...),
    chatbot_topic: str = Form(...),
    data_source: str = Form(...),
    use_case: str = Form(...),
    additional_specs: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        db_lead = Lead(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            profession=profession,
            chatbot_topic=chatbot_topic,
            data_source=data_source,
            use_case=use_case,
            additional_specs=additional_specs
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)

        html_content = load_template("form.html", {
            "success_message": "Thank you! Your inquiry has been submitted successfully. We'll contact you soon.",
            "show_success": "true"
        })
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        db.rollback()
        html_content = load_template("form.html", {
            "error_message": f"An error occurred: {str(e)}",
            "show_error": "true"
        })
        return HTMLResponse(content=html_content)

# Add a route to test CSS serving
@app.get("/test-css")
async def test_css():
    """Test if CSS is being served correctly"""
    css_path = STATIC_DIR / "css" / "style.css"
    return {
        "css_file_exists": css_path.exists(),
        "css_path": str(css_path),
        "static_dir": str(STATIC_DIR),
        "css_url": "/static/css/style.css"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)