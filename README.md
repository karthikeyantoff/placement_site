# Placement Management System (PMS) 🎓💼

A modern, high-performance, role-based placement management platform built with **Flask**, **Tailwind CSS**, **JavaScript**, **MongoDB** (with automatic local MongoMock fallback), **Cloudinary** media storage, **ReportLab** PDF engines, and **PyPDF** AI-assisted resume matcher.

---

## ✨ Features & Modules

- 🔐 **Role-Based Access Control (RBAC)**:
  - **Admin (`sivasubramaniyan` / `sivu@12345`)**: Full system governance, placement verification approvals/rejections, complete student directory CRUD, and global report analytics.
  - **Manager (`jeyakannan` / `jk@12345`)**: Candidate directory management, drive selection updates, bulk department matching, and proposal forwarding to Admin.
  - **Sourcing Leads (`lead-1` to `lead-10` / `lead1@12345`)**: Company pipeline tracking (COLD, WARM, HOT, DRIVE COMPLETED), draft saving, and verification forwarding.

- 📄 **Resume Matcher & Skill Check Engine**:
  - Upload PDF/TXT Resumes or paste file URLs.
  - Upload Job Descriptions (JD) or paste text.
  - Analyzes keyword token overlap, skill density, and experience matching.
  - **Individual & Department/Overall Bulk Scans** (filter scores by department e.g. CSE, IT, ECE, or scan all registered candidates).

- 📊 **Analytics & PDF Export Hub**:
  - Dynamic interactive histograms for matching quality brackets (91-100%, 81-90%, 71-80%, etc.).
  - **ReportLab Algorithmic PDF Exporter**: Generate instant downloadable PDF summary dossiers for any report layout.
  - **In-App Proposal Forwarding**: Compose email remarks with attached filtered student/company records and dispatch them to user inboxes.

- 🖼️ **360° Candidate Profile Audit**:
  - Detailed student profiles rendering academic CGPA / percentage indicators, department tags, contact numbers, and photo attachments.
  - Case-insensitive registration number lookups (e.g. `23cs001` or `23CS001`).

---

## 🔑 Demo Accounts Matrix

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Admin** | `sivasubramaniyan` | `sivu@12345` | Super-Admin / Approval Authority |
| **Manager** | `jeyakannan` | `jk@12345` | Academic & Placements Manager |
| **Sourcing Lead** | `lead-1` | `lead1@12345` | Lead Sourcing Agent |

---

## 🚀 Quick Start (Local Run)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/karthikeyantoff/placement_site.git
   cd placement_site
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```
   *Note: If MongoDB is not running locally, the application automatically initializes an in-memory MongoMock database seeded with 50 students, 25 companies, 18 placements, and notifications!*

4. Open `http://127.0.0.1:5000` in your web browser.

---

## ⚡ Deployment on Vercel

The repository contains pre-configured serverless descriptors (`vercel.json` & `wsgi.py`).

1. Import the repository into [Vercel](https://vercel.com/new).
2. Vercel automatically detects `vercel.json` and `@vercel/python` builder.
3. Click **Deploy**!

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, PyMongo, MongoMock, ReportLab, PyPDF, Python-dotenv
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), Tailwind CSS, Glassmorphism UI
- **Storage**: MongoDB / MongoMock, Cloudinary Media API
