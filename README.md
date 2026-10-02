# 🛠️ E-FIX HUB — Enterprise E-Waste Refurbishment Platform

**Version**: 2.0.0 (Rebuild Complete)  
**Status**: 🚀 PRODUCTION READY  
**Primary Tech Stack**: Django 6.0.1, SQLite/PostgreSQL, Tailwind CSS  

---

## 📋 PLATFORM OVERVIEW

E-Fix Hub is a **Circular Economy Platform** designed to manage the entire lifecycle of e-waste recovery and technical refurbishment. It connects Customers, Field Agents, and Restoration Engineers through a sophisticated 15-stage workflow logic to ensure maximum asset recovery and market redistribution.

---

## 🏗️ SYSTEM ARCHITECTURE

The platform implements a **Role-Based Access Control (RBAC)** architecture with the following stakeholder nodes:

- **👑 Admin (The Controller)**: Total platform oversight, logistical assignment, financial audits, and market injection.
- **📱 Customer (The Source/Buyer)**: Submits recovery assets, tracks restoration progress, and purchases certified refurbished hardware.
- **🚚 Agent (The Logistics Node)**: Field operations including physical asset collection and final order delivery.
- **🔧 Mechanic (The Engineering Node)**: Technical device restoration, progress tracking, and detailed repair logging.

---

## 🔄 THE 15-STAGE LIFECYCLE PIPELINE

The core engine enforces a strict state machine:
1.  **Upload** → 2. **Review** → 3. **Approve** → 4. **Assign Agent** → 5. **Collect** → 
6.  **Assign Mechanic** → 7. **Repair (0-100%)** → 8. **Milestone** → 9. **Complete** → 
10. **Admin Audit** → 11. **Inject to Store** → 12. **Market Listing** → 13. **Order** → 
14. **Final Dispatch** → 15. **Chain Closure**

---

## 🚀 GETTING STARTED (DEVELOPER-MODE)

### 1. Requirements
Ensure you have Python 3.10+ installed.
```bash
pip install -r requirements.txt
```

### 2. Operational Reset (Rebuild Mode)
To reset the system to its elite "Production Demo" state:
```bash
python seed_demo_data.py
python manage.py runserver
```

### 3. Integrated Test Suite
The platform includes 38 verified test cases covering every role and workflow:
```bash
python manage.py test
```

### 4. Admin Credentials (Demo)
- **URL**: [http://localhost:8000/admin-panel/](http://localhost:8000/admin-panel/)
- **Username**: `admin`
- **Password**: `admin123`

---

## 🔐 SECURITY & AUDITING

-   **High-Fidelity Audit Logs**: Every administrative and logistical action for every asset is recorded in the `ActivityLog`.
-   **Chain of Custody**: Electronic signatures (Status transitions) ensure a legally auditable history for every device.
-   **RBAC**: Strict decorators ensure that Agents cannot access Admin dashboards and Customers cannot see technical repair costs.

---

## 🛠️ MAINTENANCE

Documentation is maintained in `jemn.md` (System Blueprint). For further architectural details, refer to the [Technical Blueprint](file:///d:/EFIXHUBNEW/jemn.md).

---
*Developed with excellence by Antigravity (Senior Software Engineer).*
