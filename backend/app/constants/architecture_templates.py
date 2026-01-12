
"""
Templates for generating architecture PDFs.
"""

ARCHITECTURE_PDF_TEMPLATE = """
# Architecture Report for {app_name}

## Executive Summary
This document presents a comprehensive analysis of the {app_name} architecture, generated through automated analysis of the repository and documentation.

**Generated on:** {generated_date}
**Complexity Score:** {complexity_score}/10
**Scalability Level:** {scalability_level}

## Architecture Context Diagram
The following section illustrates the high-level context of the system, showing interactions between users, frontend, backend services, and external systems.

**System Boundaries:**
- **Frontend:** {frontend_tech}
- **Backend:** {backend_tech}
- **Database:** {database_tech}

## Frontend Architecture
**Framework & Structure:**
- **Primary Framework:** {frontend_framework}
- **Component Analysis:** {component_count} components detected.

## Backend Architecture
**Framework & Structure:**
- **Primary Framework:** {backend_framework}
- **API Endpoints:** {endpoint_count} endpoints detected.

### Detected Endpoints
{endpoints_list}

## Database Details
**Primary Database:** {primary_database}
**ORM Layer:** {orm_layer}

### Schema Overview
{database_schema}

## Security Model
**Recommendations:**
- Implement JWT token authentication
- Use HTTPS for all communications
- Validate and sanitize user inputs
- Regular security audits

## Recommendations & Next Steps
1. Implement containerization with Docker
2. Add comprehensive testing framework
3. Implement monitoring and logging
4. Add error handling and validation
5. Regular security audits and updates
"""
