from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_TITLE, APP_VERSION
from app.database import ensure_db

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event() -> None:
    ensure_db()

@app.get("/")
async def root() -> dict:
    return {
        "project": APP_TITLE,
        "version": APP_VERSION,
        "description": "Blockchain-anchored cybersecurity evidence management backend",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": APP_TITLE,
    }

from app.database import get_dashboard_summary, get_all_evidence, get_evidence_by_id, insert_evidence, get_blockchain_chain
from app.blockchain import create_block_hash, hash_bytes, generate_payload_hash, get_previous_hash
from app.tamper_detection import TamperDetector
from fastapi import Form, File, UploadFile
from typing import Optional


@app.post("/api/evidence/submit")
async def submit_evidence(
    case_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    evidence_type: str = Form(...),
    source: str = Form(...),
    severity: str = Form("medium"),
    submitted_by: str = Form("analyst"),
    file: Optional[UploadFile] = File(None),
) -> dict:
    file_bytes = await file.read() if file is not None else b""
    payload_hash = generate_payload_hash(
        {
            "case_id": case_id,
            "title": title,
            "description": description,
            "evidence_type": evidence_type,
            "source": source,
            "severity": severity,
            "submitted_by": submitted_by,
        }
    )

    file_hash = hash_bytes(file_bytes) if file_bytes else payload_hash
    previous_hash = get_previous_hash()
    chain_hash = create_block_hash(previous_hash, payload_hash, file_hash)

    evidence_data = {
        "case_id": case_id,
        "title": title,
        "description": description,
        "evidence_type": evidence_type,
        "source": source,
        "severity": severity,
        "submitted_by": submitted_by,
        "file_name": file.filename if file else None,
        "file_hash": file_hash,
        "payload_hash": payload_hash,
        "chain_hash": chain_hash,
        "previous_hash": previous_hash,
        "submitted_at": __import__("datetime").datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

    evidence_id = insert_evidence(evidence_data)
    detector = TamperDetector()
    risk = detector.analyze(evidence_data)

    return {
        "message": "Evidence anchored successfully",
        "evidence_id": evidence_id,
        "case_id": case_id,
        "title": title,
        "file_hash": file_hash,
        "payload_hash": payload_hash,
        "previous_hash": previous_hash,
        "chain_hash": chain_hash,
        "risk": risk,
    }


@app.get("/api/evidence")
async def get_evidence() -> list:
    return get_all_evidence()


@app.get("/api/evidence/{evidence_id}")
async def get_single_evidence(evidence_id: int) -> dict:
    evidence = get_evidence_by_id(evidence_id)
    if evidence is None:
        return {"detail": "Evidence not found"}
    return evidence


@app.post("/api/evidence/{evidence_id}/verify")
async def verify_evidence(evidence_id: int) -> dict:
    evidence = get_evidence_by_id(evidence_id)
    if evidence is None:
        return {"detail": "Evidence not found"}

    detector = TamperDetector()
    result = detector.verify_record(evidence)
    return result


@app.get("/api/chain")
async def get_chain() -> list:
    return get_blockchain_chain()


@app.get("/api/dashboard/summary")
async def dashboard_summary() -> dict:
    return get_dashboard_summary()
