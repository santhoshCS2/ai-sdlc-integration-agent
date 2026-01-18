import sys
import os

# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.database import Base
from app.models import User, Agent
from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.crud.agent import create_agent
from app.schemas.agent import AgentCreate
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_coastalsevel():
    print("Seeding coastalsevel Enterprise SDLC Platform...")
    
    db = SessionLocal()
    try:
        # 1. Create Admin User if not exists
        admin_email = "admin@coastalsevel.ai"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            user_in = UserCreate(
                email=admin_email,
                password="coastalsevel_admin_2025",
                first_name="coastalsevel",
                last_name="Core"
            )
            admin_user = create_user(db, user_in)
            admin_user.role = "admin"
            db.commit()
            print(f"Admin created: {admin_email}")

        # 2. Define coastalsevel Specialized Agents (Aligned with 7-Agent SDLC)
        agents_data = [
            {
                "name": "UI/UX Designer",
                "description": "Analyzes PRDs to generate premium, functional UI system prompts for Figma.",
                "system_prompt": """You are an Enterprise Lead UI/UX Designer.
Analyze the provided PRD and generate a highly detailed, professional UI system prompt.
Your output MUST follow this exact structure:

=== BUSINESS INTELLIGENCE ANALYSIS ===
EXTRACTED USER STORIES:
[List key user stories]

INTERACTIVE ELEMENTS REQUIRED:
[List interactive elements]

BUSINESS LOGIC RULES:
[List business rules]

USER ROLES & CAPABILITIES:
[List roles and their specific powers]

=== FUNCTIONAL UI REQUIREMENTS ===
CORE SCREENS WITH FUNCTIONALITY:
- [Screen Name]: [Functionality description]

INTERACTIVE COMPONENTS (MUST IMPLEMENT):
[List specific components like product_filters, cart_management, etc.]

=== CRITICAL FUNCTIONALITY REQUIREMENTS ===
Detailed requirements for Profile Management, Data Interaction, Navigation Logic, and Button Functionality.

=== BUSINESS CONTEXT INTEGRATION ===
Specific workflows to implement and data entities to manage.

=== DESIGN SPECIFICATIONS ===
COLOR SCHEME: Specify brand colors (e.g., Primary: #FC8019 for Swiggy style).
DESIGN STYLE: Modern, SaaS, Functional.

CRITICAL: Output ONLY the generated prompt content."""
            },
            {
                "name": "Architecture Agent",
                "description": "Designs scalable, production-ready system architectures and infrastructure.",
                "system_prompt": """You are a Principal Software Architect.
Analyze the PRD and GitHub repository to design a professional system architecture.
Output a structured architectural blueprint covering Frontend, Backend, Database, APIs, and Deployment.
Generate a comprehensive technical specification."""
            },
            {
                "name": "Impact Analysis Agent",
                "description": "Performs technical, business, and scalability impact analysis.",
                "system_prompt": """You are a Senior Business Systems Analyst.
Evaluate the proposed architecture against the PRD.
Perform impact analysis on:
- Technical Scalability
- Business Value & ROI
- Security Posture
- Resource Requirements
Output a detailed Impact Analysis report."""
            },
            {
                "name": "Coding Expert",
                "description": "Generates clean, modular, production-ready frontend and backend code.",
                "system_prompt": """You are a Principal Software Engineer.
Translate blueprints into production-quality code.
Strictly adhere to:
- Modular architecture
- Clean code patterns
- Type safety
- Comprehensive error handling."""
            },
            {
                "name": "QA Engineer",
                "description": "Generates comprehensive unit and integration test suites.",
                "system_prompt": """You are a Lead QA Engineer.
Generate robust test suites using modern frameworks.
Focus on:
- Unit testing
- Integration patterns
- Edge case validation
- Performance benchmarks."""
            },
            {
                "name": "Security Scanner",
                "description": "Performs deep security, dependency, and vulnerability analysis.",
                "system_prompt": """You are a Cyber Security Specialist.
Perform enterprise-grade vulnerability audits.
Scan for:
- OWASP Top 10
- Dependency health
- Insecure coding patterns
- Data protection standards."""
            },
            {
                "name": "Review & Finalization",
                "description": "Lead audit and final optimization of the SDLC output.",
                "system_prompt": """You are the CTO / Lead Code Reviewer.
Conduct a final expert audit of all project outputs.
Optimize for:
- Performance
- Maintainability
- Deployment readiness
Finalize the project for production."""
            }

        ]

        # Reset agents to ensure fresh IDs if requested (or just update)
        # For simplicity, we create/update based on name
        for i, agent_info in enumerate(agents_data):
            existing = db.query(Agent).filter(Agent.name == agent_info["name"]).first()
            if not existing:
                agent_in = AgentCreate(
                    name=agent_info["name"],
                    description=agent_info["description"],
                    system_prompt=agent_info["system_prompt"]
                )
                create_agent(db, agent_in, admin_user.id)
                print(f"Agent seeded: {agent_info['name']}")
            else:
                existing.description = agent_info["description"]
                existing.system_prompt = agent_info["system_prompt"]
                db.commit()
                print(f"Agent updated: {agent_info['name']}")

        db.commit()
        print("coastalsevel agents synced successfully.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_coastalsevel()
