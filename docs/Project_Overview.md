
# PROJECT_IMPLEMENTATION_GUIDE.md

## 1. Project Overview

### Project Name

Purchase Order Import System

### Goal

Develop a desktop application that automates importing Purchase Orders from Excel into Odoo using XML-RPC.

The application should allow a non-technical user to place Excel files into an Import folder and import them into Odoo with minimal interaction.

The application must prioritize:

* correctness
* maintainability
* modularity
* recoverability
* clear error reporting

---

## 2. High Level Workflow

```
User
    │
    ▼
Select Excel File
    │
    ▼
ExcelReader
    │
    ▼
ExcelValidator
    │
    ▼
RowMapper
    │
    ▼
ImportController
    │
    ├──────────────► PartnerService
    │
    ├──────────────► ProductService
    │
    ├──────────────► PurchaseOrderService
    │
    ▼
OdooClient
    │
XML-RPC
    │
    ▼
Odoo Server
```

---

# 3. Project Architecture

Describe every layer.

### GUI Layer

Responsibilities

* User interaction
* File selection
* Progress bar
* Display logs
* Display results

Never:

* Read Excel
* Call XML-RPC directly
* Validate data

---

### Controller Layer

This is the brain.

Responsibilities

* Coordinate the entire import
* Call services
* Handle rollback
* Group rows
* Report errors
* Update GUI

Never

* Know XML-RPC details
* Parse Excel itself

---

### Excel Layer

Responsibilities

* Read workbook
* Convert rows
* Validate fields
* Produce clean Python objects

Never

* Communicate with Odoo

---

### Service Layer

Responsibilities

Communicate with Odoo only.

Examples

PartnerService

ProductService

PurchaseOrderService

Never

* Read Excel
* Display UI
* Perform business workflow

---

### Connection Layer

OdooClient

Responsibilities

Only XML-RPC.

Should expose generic wrappers

```
search()

read()

search_read()

create()

write()

unlink()

execute_method()
```

Nothing else.

---

## 4. Dependency Rules

Strict dependency graph.

```
GUI
↓

Controller
↓

Services
↓

OdooClient
↓

Odoo
```

Allowed.

```
GUI
↓

Excel
```

Not allowed.

```
GUI
↓

OdooClient
```

Not allowed.

```
Service
↓

Excel
```

Never.

---

# 5. Data Flow

```
Excel

↓

Validated Row

↓

Mapped Row

↓

Resolved IDs

↓

Purchase Order DTO

↓

PurchaseOrderService

↓

Odoo
```

---

# 6. Folder Structure

```
project/

config/

connection/

excel/

services/

controllers/

gui/

utils/

tests/

main.py
```

Explain each folder.

---

# 7. Responsibilities of Each Module

Explain

OdooClient

PartnerService

ProductService

PurchaseOrderService

ImportController

Logger

FileManager

GUI

Main

ExcelReader

Validator

Mapper

---

# 8. Coding Standards

Use

* type hints
* docstrings
* small methods
* descriptive names
* composition over inheritance
* dependency injection

Avoid

* globals
* duplicated code
* magic numbers
* long methods

---

# 9. Error Handling Philosophy

Validation errors

↓

Controller

↓

GUI

Connection errors

↓

Raise

↓

Controller

↓

GUI

Never swallow exceptions.

---

# 10. Logging Philosophy

Every important event.

Example

```
Connected to Odoo

Reading workbook

Validating rows

Vendor found

Product found

Creating PO

PO Created

Rollback

Finished
```

---

# 11. Rollback Rules

If ANY line fails

↓

Delete created PO

↓

Keep Excel

↓

Report error

Never create partial POs.

---

# 12. Future Scalability

Future versions may include

* Multiple Excel formats
* Multiple ERP systems
* Background workers
* Batch processing
* Async imports

Current implementation should not prevent these.

---

# 13. Development Principles

Every phase should

* fit existing architecture
* avoid breaking APIs
* minimize coupling
* maximize cohesion

If uncertain

STOP

Ask questions

Never guess.

---

# 14. Phase Development Workflow

For every implementation phase:

1. Read this document.
2. Read the existing code.
3. Understand dependencies.
4. List assumptions.
5. Ask questions if needed.
6. Produce an implementation plan.
7. Wait for approval.
8. Implement.
9. Explain integration.
10. Do not modify unrelated files.

---

# Current Project Status

Completed

- Configuration layer
- OdooClient
- ExcelReader
- ExcelValidator
- RowMapper
- PartnerService
- ProductService

In Progress

- PurchaseOrderService

Planned

- ImportController
- Logging
- FileManager
- GUI
- Main application wiring

---

# Final Principle

The objective is **not just to generate code**.

The objective is to build a maintainable, production-quality application.

Every implementation should integrate naturally with the existing architecture, minimize future refactoring, and preserve clean separation of responsibilities.
