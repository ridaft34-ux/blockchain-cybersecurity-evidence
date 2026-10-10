# Blockchain-Anchored Cybersecurity Evidence Submission with AI-Powered Tamper Detection

This repository contains a Python backend mini-project for a cybersecurity evidence management system. It demonstrates how digital evidence can be submitted, hashed, chained in a blockchain-like ledger, and continuously checked for tampering using an AI-inspired anomaly engine.

## Project Idea

Organizations and forensic teams often need to preserve, validate, and investigate digital evidence while maintaining integrity. This project simulates a secure evidence submission system where:

- Each evidence item is assigned a cryptographic hash
- A previous-hash linkage creates a blockchain-style chain
- Evidence entries are stored in SQLite
- Automated tamper detection checks integrity and risk levels
- AI-inspired scoring identifies suspicious anomalies

## Features

- Secure evidence submission through a FastAPI backend
- SHA-256 hashing for evidence and block integrity
- Blockchain-style chaining using previous block hashes
- SQLite persistence for evidence and ledger entries
- Tamper detection engine with risk scoring
- Verification endpoint for evidence authenticity checks
- Summary dashboard for analyzers
- Backend-only implementation in Python

## Tech Stack

- Python 3.11+
- FastAPI
- Uvicorn
- SQLite
- Pydantic
- Python-Multipart

## Project Structure

```text
blockchain-cybersecurity-evidence/
├── app/
│   ├── __init__.py
│   ├── blockchain.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   └── tamper_detection.py
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└── data/
    └── .gitkeep
```

## Installation

1. Clone the repository
2. Open the project folder
3. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Endpoints

### 1. Health Check

```http
GET /health
```

### 2. Submit Evidence

```http
POST /api/evidence/submit
```

Form fields:
- case_id
- title
- description
- evidence_type
- source
- severity
- submitted_by
- file (optional)

### 3. Get All Evidence

```http
GET /api/evidence
```

### 4. Get Single Evidence Record

```http
GET /api/evidence/{evidence_id}
```

### 5. Verify Evidence Integrity

```http
POST /api/evidence/{evidence_id}/verify
```

### 6. Get Blockchain Ledger

```http
GET /api/chain
```

### 7. Dashboard Summary

```http
GET /api/dashboard/summary
```

## Example JSON Response

```json
{
  "message": "Evidence anchored successfully",
  "evidence_id": 1,
  "case_id": "CASE-101",
  "title": "Firewall log snapshot",
  "file_hash": "9d2d...",
  "chain_hash": "61c3...",
  "previous_hash": "bdaf...",
  "risk": {
    "score": 20,
    "status": "watch",
    "reasons": [
      "Evidence source is external and should be validated manually"
    ],
    "ai_model": "evidence-integrity-risk-model-v1"
  }
}
```

## How Tamper Detection Works

The tamper detection module evaluates a set of risk indicators, including:

- unusual or missing file hashing
- suspicious source or severity patterns
- unexpected content anomalies
- chain mismatch detection
- evidence quality issues

The system calculates a risk score from 0 to 100 and assigns a status:

- clean
- watch
- suspicious
- critical

## Project Scope and Learning Value

This mini-project is suitable for a final-year academic submission because it combines:

- cybersecurity fundamentals
- data integrity assurance
- blockchain concepts
- API and database design
- anomaly detection logic
- practical Python implementation

## Future Enhancements

- Add JWT authentication
- Protect endpoints with role-based access
- Support larger evidence files and cloud storage
- Integrate real ML models for anomaly detection
- Add audit trails and user roles
- Build a frontend dashboard in a different layer if required later

## License

This project is free to use for educational and academic purposes.
