import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "evidence.db"


def ensure_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            evidence_type TEXT,
            source TEXT,
            severity TEXT,
            submitted_by TEXT,
            file_name TEXT,
            file_hash TEXT,
            payload_hash TEXT,
            chain_hash TEXT,
            previous_hash TEXT,
            submitted_at TEXT,
            metadata TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blockchain (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER,
            previous_hash TEXT,
            current_hash TEXT,
            payload_hash TEXT,
            file_hash TEXT,
            timestamp TEXT,
            metadata TEXT,
            FOREIGN KEY (evidence_id) REFERENCES evidence(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id INTEGER,
            event_type TEXT,
            status TEXT,
            risk_score INTEGER,
            details TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert_evidence(evidence_data: Dict[str, Any]) -> int:
    conn = get_connection()
    cur = conn.cursor()
    metadata = json.dumps({
        "file_name": evidence_data.get("file_name"),
        "source": evidence_data.get("source"),
        "evidence_type": evidence_data.get("evidence_type"),
        "severity": evidence_data.get("severity"),
    })
    cur.execute(
        """
        INSERT INTO evidence (
            case_id, title, description, evidence_type, source, severity,
            submitted_by, file_name, file_hash, payload_hash, chain_hash,
            previous_hash, submitted_at, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evidence_data["case_id"],
            evidence_data["title"],
            evidence_data.get("description", ""),
            evidence_data.get("evidence_type", "unknown"),
            evidence_data.get("source", "internal"),
            evidence_data.get("severity", "medium"),
            evidence_data.get("submitted_by", "analyst"),
            evidence_data.get("file_name"),
            evidence_data.get("file_hash"),
            evidence_data.get("payload_hash"),
            evidence_data.get("chain_hash"),
            evidence_data.get("previous_hash"),
            evidence_data.get("submitted_at"),
            metadata,
        ),
    )
    evidence_id = cur.lastrowid
    cur.execute(
        """
        INSERT INTO blockchain (
            evidence_id, previous_hash, current_hash, payload_hash, file_hash,
            timestamp, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            evidence_id,
            evidence_data.get("previous_hash"),
            evidence_data.get("chain_hash"),
            evidence_data.get("payload_hash"),
            evidence_data.get("file_hash"),
            evidence_data.get("submitted_at"),
            metadata,
        ),
    )
    conn.commit()
    conn.close()
    return evidence_id


def get_all_evidence() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM evidence ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_evidence_by_id(evidence_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def get_blockchain_chain() -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM blockchain ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_dashboard_summary() -> Dict[str, Any]:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
    critical = conn.execute("SELECT COUNT(*) FROM evidence WHERE severity = 'critical'").fetchone()[0]
    suspicious = conn.execute("SELECT COUNT(*) FROM evidence WHERE source = 'external'").fetchone()[0]
    last = conn.execute("SELECT MAX(id) FROM evidence").fetchone()[0]
    conn.close()
    return {
        "total_evidence": total,
        "critical_cases": critical,
        "external_sources": suspicious,
        "latest_entry_id": last,
        "system": "Blockchain Evidence Security API",
    }
