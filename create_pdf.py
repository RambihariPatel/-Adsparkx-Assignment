"""
Script to generate saas_api_guide.pdf for NexaCloud knowledge base.
Run this once to create the required PDF document.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import os

# Color palette
PRIMARY = HexColor('#4F46E5')    # Indigo
SECONDARY = HexColor('#7C3AED')  # Purple
DARK = HexColor('#1E1B4B')       # Dark navy
LIGHT_BG = HexColor('#F5F3FF')   # Light lavender
CODE_BG = HexColor('#1E293B')    # Dark slate (code blocks)
CODE_FG = HexColor('#E2E8F0')    # Light slate (code text)
ACCENT = HexColor('#06B6D4')     # Cyan
SUCCESS = HexColor('#10B981')    # Emerald
WARNING = HexColor('#F59E0B')    # Amber
ERROR_COLOR = HexColor('#EF4444')# Red
BORDER = HexColor('#DDD6FE')     # Light purple border

def create_styles():
    styles = getSampleStyleSheet()
    
    custom = {
        'Title': ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=28,
                                 textColor=DARK, spaceAfter=6, alignment=TA_CENTER),
        'Subtitle': ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=14,
                                    textColor=SECONDARY, spaceAfter=4, alignment=TA_CENTER),
        'ArticleId': ParagraphStyle('ArticleId', fontName='Helvetica', fontSize=10,
                                     textColor=HexColor('#6B7280'), alignment=TA_CENTER, spaceAfter=20),
        'H1': ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=20,
                              textColor=PRIMARY, spaceBefore=20, spaceAfter=10,
                              borderPad=6),
        'H2': ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=15,
                              textColor=DARK, spaceBefore=16, spaceAfter=8),
        'H3': ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=12,
                              textColor=SECONDARY, spaceBefore=10, spaceAfter=6),
        'Body': ParagraphStyle('Body', fontName='Helvetica', fontSize=10,
                                textColor=HexColor('#374151'), leading=16, spaceAfter=6,
                                alignment=TA_JUSTIFY),
        'Bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=10,
                                  textColor=HexColor('#374151'), leading=16,
                                  leftIndent=20, spaceAfter=4),
        'Code': ParagraphStyle('Code', fontName='Courier', fontSize=9,
                                textColor=CODE_FG, backColor=CODE_BG,
                                leading=14, leftIndent=10, rightIndent=10,
                                spaceAfter=10, spaceBefore=6,
                                borderPad=8),
        'CodeInline': ParagraphStyle('CodeInline', fontName='Courier', fontSize=9,
                                      textColor=SECONDARY),
        'Note': ParagraphStyle('Note', fontName='Helvetica-Oblique', fontSize=10,
                                textColor=HexColor('#6B7280'), leading=14,
                                leftIndent=10, spaceBefore=4, spaceAfter=8),
        'Footer': ParagraphStyle('Footer', fontName='Helvetica', fontSize=8,
                                  textColor=HexColor('#9CA3AF'), alignment=TA_CENTER),
    }
    return custom

def make_section_table(content_rows, col_widths=None):
    """Helper to create a styled table."""
    table = Table(content_rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_BG]),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    return table

def add_header_footer(canvas, doc):
    """Add header and footer to each page."""
    canvas.saveState()
    page_num = canvas.getPageNumber()
    
    # Header bar
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, A4[1] - 40, A4[0], 40, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawString(2*cm, A4[1] - 27, 'NexaCloud')
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(A4[0] - 2*cm, A4[1] - 27, 'API Reference Guide | Confidential')
    
    # Footer
    canvas.setFillColor(HexColor('#9CA3AF'))
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(A4[0]/2, 1.5*cm, f'NexaCloud API Reference Guide (API-001) — Page {page_num}')
    canvas.drawString(2*cm, 1.5*cm, 'docs.nexacloud.io')
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, '© 2025 NexaCloud Technologies Pvt. Ltd.')
    
    # Footer line
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 2*cm, A4[0] - 2*cm, 2*cm)
    
    canvas.restoreState()

def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=3*cm,
        bottomMargin=2.5*cm,
        leftMargin=2*cm,
        rightMargin=2*cm,
        title='NexaCloud API Reference Guide',
        author='NexaCloud Support Team',
        subject='Complete API Reference and Integration Documentation',
    )
    
    S = create_styles()
    story = []

    # ─── COVER PAGE ──────────────────────────────────────────────
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph('NexaCloud', S['Title']))
    story.append(Paragraph('API Reference Guide', S['Subtitle']))
    story.append(Paragraph('Article ID: API-001 | Version 2.4 | Last Updated: June 2025', S['ArticleId']))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=20))
    
    intro_text = (
        "This document provides a complete reference for the NexaCloud REST API. "
        "It covers authentication, all available endpoints, request/response formats, "
        "error handling, and code examples in Python, JavaScript, and cURL. "
        "The NexaCloud API is RESTful, uses JSON for request/response bodies, "
        "and authenticates via Bearer tokens. All requests must be made over HTTPS."
    )
    story.append(Paragraph(intro_text, S['Body']))
    story.append(Spacer(1, 0.5*cm))
    
    # Quick Reference Table
    quick_ref = [
        ['Property', 'Value'],
        ['Base URL', 'https://api.nexacloud.io/v1'],
        ['Protocol', 'HTTPS only (TLS 1.2+)'],
        ['Format', 'JSON (application/json)'],
        ['Authentication', 'Bearer Token (API Key)'],
        ['Rate Limiting', 'Per plan (see Rate Limiting Guide API-002)'],
        ['Versioning', 'URL path versioning (/v1, /v2)'],
        ['Pagination', 'Cursor-based (page + per_page)'],
        ['Timestamps', 'ISO 8601 / UTC (YYYY-MM-DDTHH:MM:SSZ)'],
    ]
    story.append(make_section_table(quick_ref, [7*cm, 10*cm]))
    story.append(PageBreak())

    # ─── SECTION 1: AUTHENTICATION ───────────────────────────────
    story.append(Paragraph('1. Authentication', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    story.append(Paragraph('1.1 API Key Authentication', S['H2']))
    story.append(Paragraph(
        'All NexaCloud API requests require authentication using an API key passed '
        'as a Bearer token in the Authorization header. API keys are scoped to specific '
        'permissions and can be created, managed, and revoked from the Settings → API Keys dashboard.',
        S['Body']
    ))
    
    story.append(Paragraph('Request Header Format:', S['H3']))
    code1 = (
        'Authorization: Bearer YOUR_API_KEY\n'
        'Content-Type: application/json\n'
        'Accept: application/json'
    )
    story.append(Paragraph(code1, S['Code']))
    
    story.append(Paragraph('Python Example:', S['H3']))
    code2 = (
        'import requests\n\n'
        'API_KEY = "nxc_live_your_api_key_here"\n'
        'BASE_URL = "https://api.nexacloud.io/v1"\n\n'
        'headers = {\n'
        '    "Authorization": f"Bearer {API_KEY}",\n'
        '    "Content-Type": "application/json"\n'
        '}\n\n'
        'response = requests.get(f"{BASE_URL}/projects", headers=headers)\n'
        'print(response.json())'
    )
    story.append(Paragraph(code2, S['Code']))
    
    story.append(Paragraph('cURL Example:', S['H3']))
    code3 = (
        'curl -X GET "https://api.nexacloud.io/v1/projects" \\\n'
        '  -H "Authorization: Bearer YOUR_API_KEY" \\\n'
        '  -H "Content-Type: application/json"'
    )
    story.append(Paragraph(code3, S['Code']))

    story.append(Paragraph('1.2 API Key Scopes', S['H2']))
    scope_table = [
        ['Scope', 'Access Level', 'Recommended Use Case'],
        ['read:all', 'Read all resources', 'Dashboards, reporting tools'],
        ['write:projects', 'Create/update projects', 'CI/CD integrations'],
        ['write:users', 'Manage users', 'User provisioning systems'],
        ['write:data', 'Write data sources', 'ETL pipelines'],
        ['admin', 'Full access', 'Backend admin systems (use with caution)'],
        ['billing:read', 'View billing info', 'Finance integrations'],
        ['webhooks', 'Manage webhooks', 'Event-driven integrations'],
    ]
    story.append(make_section_table(scope_table, [4*cm, 4*cm, 9*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        '⚠️  Security Note: Always use the minimum required scope. '
        'Rotate API keys every 90 days. Never commit API keys to source control — '
        'use environment variables or secrets management tools.',
        S['Note']
    ))

    story.append(PageBreak())

    # ─── SECTION 2: PROJECTS ENDPOINTS ──────────────────────────
    story.append(Paragraph('2. Projects API', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    endpoints_data = [
        ['Method', 'Endpoint', 'Description', 'Scope Required'],
        ['GET', '/v1/projects', 'List all projects', 'read:all'],
        ['POST', '/v1/projects', 'Create a new project', 'write:projects'],
        ['GET', '/v1/projects/{id}', 'Get project by ID', 'read:all'],
        ['PUT', '/v1/projects/{id}', 'Update project', 'write:projects'],
        ['DELETE', '/v1/projects/{id}', 'Delete project', 'admin'],
        ['GET', '/v1/projects/{id}/members', 'List project members', 'read:all'],
        ['POST', '/v1/projects/{id}/members', 'Add member to project', 'write:projects'],
    ]
    story.append(make_section_table(endpoints_data, [2*cm, 5.5*cm, 5.5*cm, 4*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph('2.1 List Projects', S['H2']))
    story.append(Paragraph('GET /v1/projects', S['H3']))
    story.append(Paragraph('Returns a paginated list of all projects in your organization.', S['Body']))
    
    story.append(Paragraph('Query Parameters:', S['H3']))
    params_table = [
        ['Parameter', 'Type', 'Required', 'Description'],
        ['page', 'integer', 'No', 'Page number (default: 1)'],
        ['per_page', 'integer', 'No', 'Items per page (default: 20, max: 100)'],
        ['status', 'string', 'No', 'Filter: active, archived, all (default: active)'],
        ['search', 'string', 'No', 'Search by project name'],
        ['sort', 'string', 'No', 'Sort field: name, created_at, updated_at'],
        ['order', 'string', 'No', 'Sort order: asc, desc (default: desc)'],
    ]
    story.append(make_section_table(params_table, [3*cm, 2.5*cm, 2.5*cm, 9*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph('Response (200 OK):', S['H3']))
    code_response = (
        '{\n'
        '  "data": [\n'
        '    {\n'
        '      "id": "proj_abc123",\n'
        '      "name": "Marketing Analytics Q2",\n'
        '      "description": "Q2 campaign performance tracking",\n'
        '      "visibility": "private",\n'
        '      "status": "active",\n'
        '      "owner": {\n'
        '        "id": "usr_def456",\n'
        '        "name": "Jane Smith",\n'
        '        "email": "jane@company.com"\n'
        '      },\n'
        '      "member_count": 5,\n'
        '      "created_at": "2025-01-15T10:30:00Z",\n'
        '      "updated_at": "2025-06-01T08:15:00Z"\n'
        '    }\n'
        '  ],\n'
        '  "pagination": {\n'
        '    "total": 42,\n'
        '    "page": 1,\n'
        '    "per_page": 20,\n'
        '    "total_pages": 3,\n'
        '    "has_next": true,\n'
        '    "next_cursor": "cursor_xyz789"\n'
        '  }\n'
        '}'
    )
    story.append(Paragraph(code_response, S['Code']))

    story.append(PageBreak())

    # ─── SECTION 3: USERS API ────────────────────────────────────
    story.append(Paragraph('3. Users API', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    user_endpoints = [
        ['Method', 'Endpoint', 'Description', 'Scope Required'],
        ['GET', '/v1/users', 'List organization users', 'read:all'],
        ['POST', '/v1/users/invite', 'Invite a new user', 'write:users'],
        ['GET', '/v1/users/{id}', 'Get user details', 'read:all'],
        ['PUT', '/v1/users/{id}', 'Update user profile/role', 'write:users'],
        ['DELETE', '/v1/users/{id}', 'Remove user from org', 'write:users'],
        ['POST', '/v1/users/{id}/deactivate', 'Deactivate user', 'write:users'],
        ['GET', '/v1/users/me', 'Get current user', 'read:all'],
    ]
    story.append(make_section_table(user_endpoints, [2*cm, 5.5*cm, 5.5*cm, 4*cm]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('3.1 Invite User', S['H2']))
    story.append(Paragraph('POST /v1/users/invite', S['H3']))
    story.append(Paragraph('Send an invitation email to a new team member.', S['Body']))
    
    story.append(Paragraph('Request Body:', S['H3']))
    invite_body = (
        '{\n'
        '  "email": "newmember@company.com",\n'
        '  "role": "member",\n'
        '  "projects": ["proj_abc123", "proj_def456"],\n'
        '  "send_welcome_email": true\n'
        '}'
    )
    story.append(Paragraph(invite_body, S['Code']))
    
    story.append(Paragraph('Response (201 Created):', S['H3']))
    invite_resp = (
        '{\n'
        '  "data": {\n'
        '    "id": "inv_ghi789",\n'
        '    "email": "newmember@company.com",\n'
        '    "role": "member",\n'
        '    "status": "pending",\n'
        '    "invited_by": "usr_def456",\n'
        '    "expires_at": "2025-06-08T10:00:00Z"\n'
        '  }\n'
        '}'
    )
    story.append(Paragraph(invite_resp, S['Code']))

    story.append(PageBreak())

    # ─── SECTION 4: DATA SOURCES API ─────────────────────────────
    story.append(Paragraph('4. Data Sources API', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    story.append(Paragraph(
        'Data Sources are connections to external databases, APIs, and services. '
        'Once connected, data is automatically synced based on the configured schedule.',
        S['Body']
    ))
    
    ds_endpoints = [
        ['Method', 'Endpoint', 'Description'],
        ['GET', '/v1/data-sources', 'List all data sources'],
        ['POST', '/v1/data-sources', 'Create a new data source'],
        ['GET', '/v1/data-sources/{id}', 'Get data source details'],
        ['PUT', '/v1/data-sources/{id}', 'Update data source config'],
        ['DELETE', '/v1/data-sources/{id}', 'Remove data source'],
        ['POST', '/v1/data-sources/{id}/sync', 'Trigger manual sync'],
        ['GET', '/v1/data-sources/{id}/sync-logs', 'View sync history'],
        ['POST', '/v1/data-sources/test', 'Test connection before saving'],
    ]
    story.append(make_section_table(ds_endpoints, [2*cm, 6.5*cm, 8.5*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph('4.1 Create PostgreSQL Data Source', S['H2']))
    story.append(Paragraph('POST /v1/data-sources', S['H3']))
    
    pg_body = (
        '{\n'
        '  "name": "Production Database",\n'
        '  "type": "postgresql",\n'
        '  "config": {\n'
        '    "host": "db.company.com",\n'
        '    "port": 5432,\n'
        '    "database": "prod_analytics",\n'
        '    "username": "nexacloud_reader",\n'
        '    "password": "encrypted_password",\n'
        '    "ssl_mode": "require"\n'
        '  },\n'
        '  "sync_frequency": "hourly",\n'
        '  "sync_tables": ["orders", "customers", "products"]\n'
        '}'
    )
    story.append(Paragraph(pg_body, S['Code']))
    
    story.append(Paragraph('4.2 Supported Data Source Types', S['H2']))
    types_table = [
        ['Type Value', 'Integration', 'Authentication Method'],
        ['postgresql', 'PostgreSQL', 'Username/Password + SSL'],
        ['mysql', 'MySQL', 'Username/Password + SSL'],
        ['bigquery', 'Google BigQuery', 'Service Account JSON'],
        ['snowflake', 'Snowflake', 'Username/Password + Account'],
        ['mongodb', 'MongoDB', 'Connection URI'],
        ['rest_api', 'Custom REST API', 'API Key / OAuth 2.0'],
        ['google_analytics', 'Google Analytics 4', 'OAuth 2.0'],
        ['salesforce', 'Salesforce', 'OAuth 2.0'],
        ['amazon_s3', 'Amazon S3', 'AWS Access Key + Secret'],
    ]
    story.append(make_section_table(types_table, [4*cm, 5*cm, 8*cm]))

    story.append(PageBreak())

    # ─── SECTION 5: WEBHOOKS & EVENTS ────────────────────────────
    story.append(Paragraph('5. Webhooks API', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    story.append(Paragraph(
        'Webhooks enable real-time event notifications to your server. '
        'See the Webhook Documentation (INT-004) for the complete list of events and payload structures.',
        S['Body']
    ))
    
    wh_endpoints = [
        ['Method', 'Endpoint', 'Description'],
        ['GET', '/v1/webhooks', 'List all webhooks'],
        ['POST', '/v1/webhooks', 'Register a new webhook'],
        ['GET', '/v1/webhooks/{id}', 'Get webhook details'],
        ['PUT', '/v1/webhooks/{id}', 'Update webhook'],
        ['DELETE', '/v1/webhooks/{id}', 'Delete webhook'],
        ['GET', '/v1/webhooks/{id}/events', 'List recent events'],
        ['POST', '/v1/webhooks/{id}/events/{event_id}/retry', 'Retry failed event'],
        ['POST', '/v1/webhooks/{id}/test', 'Send test event'],
    ]
    story.append(make_section_table(wh_endpoints, [2*cm, 6.5*cm, 8.5*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph('5.1 Create Webhook', S['H2']))
    wh_body = (
        'POST /v1/webhooks\n\n'
        '{\n'
        '  "url": "https://your-server.com/webhooks/nexacloud",\n'
        '  "events": [\n'
        '    "project.created",\n'
        '    "report.generated",\n'
        '    "alert.triggered",\n'
        '    "integration.sync_failed"\n'
        '  ],\n'
        '  "secret": "your_hmac_secret_256bit",\n'
        '  "active": true,\n'
        '  "description": "Production event handler"\n'
        '}'
    )
    story.append(Paragraph(wh_body, S['Code']))

    story.append(PageBreak())

    # ─── SECTION 6: ERROR HANDLING ───────────────────────────────
    story.append(Paragraph('6. Error Handling', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    story.append(Paragraph(
        'All errors follow a consistent format. HTTP status codes indicate the class of error, '
        'while the error code provides specific details. See the Error Codes Reference (API-003) '
        'for the complete list of error codes and remediation steps.',
        S['Body']
    ))
    
    story.append(Paragraph('Standard Error Response Format:', S['H3']))
    err_resp = (
        '{\n'
        '  "error": {\n'
        '    "code": "AUTH_002",\n'
        '    "message": "Invalid API key provided.",\n'
        '    "details": "The API key does not exist or has been revoked.",\n'
        '    "request_id": "req_9f3a2b1c4d5e",\n'
        '    "documentation_url": "https://docs.nexacloud.io/errors/AUTH_002"\n'
        '  }\n'
        '}'
    )
    story.append(Paragraph(err_resp, S['Code']))
    
    story.append(Paragraph('HTTP Status Code Summary:', S['H2']))
    status_table = [
        ['Status Code', 'Meaning', 'Common Cause'],
        ['200 OK', 'Success', 'Request completed normally'],
        ['201 Created', 'Resource created', 'POST request succeeded'],
        ['204 No Content', 'Success, no body', 'DELETE request succeeded'],
        ['400 Bad Request', 'Invalid request', 'Missing or malformed parameters'],
        ['401 Unauthorized', 'Auth failed', 'Missing/invalid/expired API key'],
        ['403 Forbidden', 'Access denied', 'Insufficient API key scope'],
        ['404 Not Found', 'Resource missing', 'Wrong ID or resource deleted'],
        ['409 Conflict', 'Resource conflict', 'Duplicate creation attempt'],
        ['422 Unprocessable', 'Validation failed', 'Field validation errors'],
        ['429 Too Many Req.', 'Rate limited', 'Exceeded plan rate limits'],
        ['500 Server Error', 'NexaCloud error', 'Retry with exponential backoff'],
        ['503 Unavailable', 'Maintenance', 'Check status.nexacloud.io'],
    ]
    story.append(make_section_table(status_table, [4*cm, 4*cm, 9*cm]))

    story.append(PageBreak())

    # ─── SECTION 7: SDK & CODE EXAMPLES ─────────────────────────
    story.append(Paragraph('7. Official SDKs & Code Examples', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    story.append(Paragraph('7.1 Python SDK', S['H2']))
    sdk_install = 'pip install nexacloud-python'
    story.append(Paragraph(sdk_install, S['Code']))
    
    story.append(Paragraph('Quick Start:', S['H3']))
    py_sdk = (
        'from nexacloud import NexaCloud\n\n'
        '# Initialize client\n'
        'client = NexaCloud(api_key="YOUR_API_KEY")\n\n'
        '# List projects\n'
        'projects = client.projects.list()\n'
        'for project in projects:\n'
        '    print(f"Project: {project.name} ({project.id})")\n\n'
        '# Create a project\n'
        'new_project = client.projects.create(\n'
        '    name="My New Dashboard",\n'
        '    visibility="private"\n'
        ')\n\n'
        '# Invite a user\n'
        'client.users.invite(\n'
        '    email="colleague@company.com",\n'
        '    role="member",\n'
        '    projects=[new_project.id]\n'
        ')'
    )
    story.append(Paragraph(py_sdk, S['Code']))
    
    story.append(Paragraph('7.2 Node.js SDK', S['H2']))
    node_install = 'npm install @nexacloud/node-sdk'
    story.append(Paragraph(node_install, S['Code']))
    
    node_sdk = (
        'const { NexaCloud } = require("@nexacloud/node-sdk");\n\n'
        'const client = new NexaCloud({ apiKey: process.env.NEXACLOUD_API_KEY });\n\n'
        '// List projects\n'
        'const { data: projects } = await client.projects.list();\n'
        'projects.forEach(p => console.log(`${p.name}: ${p.id}`));\n\n'
        '// Trigger sync\n'
        'await client.dataSources.sync("ds_abc123");\n'
        'console.log("Sync triggered successfully");'
    )
    story.append(Paragraph(node_sdk, S['Code']))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        'Additional SDKs available: Ruby, Go, Java, PHP. '
        'Full SDK documentation at: docs.nexacloud.io/sdks',
        S['Note']
    ))

    story.append(PageBreak())

    # ─── SECTION 8: CHANGELOG ────────────────────────────────────
    story.append(Paragraph('8. API Changelog', S['H1']))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    
    changelog = [
        ['Version', 'Date', 'Changes'],
        ['v2.4', 'June 2025', 'Added cursor-based pagination; new /v1/usage/rate-limits endpoint'],
        ['v2.3', 'March 2025', 'Webhook retry improvements; FIDO2 key management endpoints'],
        ['v2.2', 'Jan 2025', 'BigQuery and Snowflake data source support added'],
        ['v2.1', 'Oct 2024', 'Custom roles API; audit log export endpoint added'],
        ['v2.0', 'July 2024', 'Breaking: unified error format; new auth scopes system'],
        ['v1.9', 'April 2024', 'GraphQL API beta; real-time WebSocket events (beta)'],
        ['v1.8', 'Jan 2024', 'HIPAA-compliant endpoints; data residency support'],
    ]
    story.append(make_section_table(changelog, [2*cm, 3*cm, 12*cm]))
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        'Breaking changes are announced 90 days in advance via email and the status page. '
        'Subscribe to API change notifications at status.nexacloud.io.',
        S['Note']
    ))
    
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=10))
    story.append(Paragraph(
        'For API support, contact api-support@nexacloud.io or visit our developer forum at community.nexacloud.io. '
        'Full interactive API documentation with live testing is available at docs.nexacloud.io/api.',
        S['Body']
    ))

    # Build the PDF
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    print(f"[OK] PDF created successfully: {output_path}")

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "saas_api_guide.pdf")
    build_pdf(output_path)
