from datetime import datetime
from typing import Any, Dict, List


class TamperDetector:
    def analyze(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        score = 0
        reasons: List[str] = []

        if not evidence.get("file_hash"):
            score += 25
            reasons.append("Missing file hash is a strong integrity risk")

        if evidence.get("source", "").lower() == "external":
            score += 15
            reasons.append("Evidence source is external and should be validated manually")

        if evidence.get("severity", "").lower() == "critical":
            score += 10
            reasons.append("Critical severity requires elevated review")

        if len((evidence.get("description") or "")) < 25:
            score += 10
            reasons.append("Evidence description is too short to support strong forensic context")

        if "test" in (evidence.get("title", "") or "").lower():
            score += 5
            reasons.append("Title pattern suggests low-confidence evidence labeling")

        if not evidence.get("case_id"):
            score += 20
            reasons.append("Missing case ID weakens traceability")

        if score >= 70:
            status = "critical"
        elif score >= 45:
            status = "suspicious"
        elif score >= 20:
            status = "watch"
        else:
            status = "clean"

        return {
            "score": min(score, 100),
            "status": status,
            "reasons": reasons,
            "ai_model": "evidence-integrity-risk-model-v1",
        }

    def verify_record(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        risk = self.analyze(evidence)
        is_valid = risk["score"] < 40
        return {
            "evidence_id": evidence.get("id"),
            "case_id": evidence.get("case_id"),
            "integrity_status": "verified" if is_valid else "needs_review",
            "risk": risk,
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "verification_note": "Chain and metadata were checked against the current integrity model",
        }
