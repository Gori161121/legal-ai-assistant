# Database Design

## Overview

The database serves as the central source of truth for legal documents, case information, workflow records, AI-generated insights, and organizational knowledge.

The design focuses on searchability, document intelligence, workflow automation, and scalable legal operations.

---

## Main Entities

### Organizations

Stores information about law firms, legal teams, or departments.

Fields:

- organization_id
- organization_name
- industry
- status

---

### Clients

Stores client information.

Fields:

- client_id
- organization_id
- full_name
- contact_information
- status

---

### Cases

Stores legal matters and case records.

Fields:

- case_id
- client_id
- title
- category
- status
- created_date

---

### Documents

Stores legal documents and metadata.

Fields:

- document_id
- case_id
- document_name
- document_type
- upload_date
- status

---

### Contracts

Stores contract-related information.

Fields:

- contract_id
- client_id
- contract_type
- effective_date
- expiration_date
- status

---

### Tasks

Stores legal workflow tasks.

Fields:

- task_id
- case_id
- assigned_to
- due_date
- status

---

### AI Insights

Stores AI-generated summaries and recommendations.

Fields:

- insight_id
- case_id
- generated_date
- summary
- recommendation
- confidence_score

---

## Database Relationships

Organizations → Clients

Clients → Cases

Cases → Documents

Cases → Tasks

Clients → Contracts

Cases → AI Insights

---

## Planned Technologies

- PostgreSQL
- MySQL
- Supabase
- Airtable

---

## Security Considerations

- role-based access control
- encrypted document storage
- audit logs
- activity tracking
- permission management

---

## Future Improvements

- vector search
- legal knowledge graph
- semantic document search
- compliance monitoring
- AI document intelligence
