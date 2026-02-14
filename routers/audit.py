from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from database import get_db,supabase
from models.ot_details import OTDetail  #
import json,io

router = APIRouter(prefix="/ot-details", tags=["OT Details"])

from models.status import Status #
from models.department import Department #
from models.ot_details import OTDetail #

@router.get("/{reference_number}")
def get_ot_full_details(reference_number: str, db: Session = Depends(get_db)):
    # Join OTDetail with Status and Department tables
    result = (
        db.query(
            OTDetail,
            Status.name.label("status_name"),
            Department.name.label("dept_name")
        )
        .outerjoin(Status, OTDetail.status_id == Status.id)
        .outerjoin(Department, OTDetail.department_id == Department.id)
        .filter(OTDetail.reference_number == reference_number)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="OT record not found")

    record, status_name, dept_name = result

    return {
        "id": str(record.id),
        "reference_number": record.reference_number,
        "ot_name": record.ot_name,
        "status_id": record.status_id,
        "status": status_name or "Unknown", # Return the mapped name
        "department_name": dept_name or "N/A", # Return the mapped name
        "amount": float(record.amount) if record.amount else 0.0,
        "comments": record.comments,
        "ot_date": record.ot_date.isoformat() if record.ot_date else None,
        "invoice_number": record.invoice_number,
        "files": record.document_path or []
    }


@router.get("/download-stream/{reference_number}/{file_name}")
def stream_file_from_supabase(reference_number: str, file_name: str):
    try:
        # 1. Check if we can even see the bucket
        buckets = supabase.storage.list_buckets()
        print(f"DEBUG: All available buckets: {[b.name for b in buckets]}")

        # 2. List everything in the root
        root_items = supabase.storage.from_("ot-documents").list()
        print(f"DEBUG: Items in root: {[i['name'] for i in root_items]}")

        # 3. Try to download
        full_path = f"{reference_number}/{file_name}"
        file_data = supabase.storage.from_("ot-documents").download(full_path)

        return StreamingResponse(io.BytesIO(file_data), media_type="application/octet-stream")

    except Exception as e:
        print(f"DEBUG FAIL: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{reference_number}/history")
def get_ot_history(reference_number: str, db: Session = Depends(get_db)):
    # Join with Status and Department to get human-readable names
    history = (
        db.query(
            OTDetail,
            Status.name.label("status_name"),
            Department.name.label("dept_name")
        )
        .outerjoin(Status, OTDetail.status_id == Status.id)
        .outerjoin(Department, OTDetail.department_id == Department.id)
        .filter(OTDetail.reference_number == reference_number)
        .order_by(OTDetail.changed_at.desc())
        .all()
    )

    return [
        {
            "ot_name": item.OTDetail.ot_name,
            "status": item.status_name or "Unknown",
            "department_name": item.dept_name or "N/A",
            "updated_at": item.OTDetail.changed_at.strftime("%d/%m/%Y %H:%M:%S") if item.OTDetail.changed_at else None,
            "ot_date": item.OTDetail.ot_date.strftime("%d/%m/%Y") if item.OTDetail.ot_date else None,
            "attachments": item.OTDetail.document_path if isinstance(item.OTDetail.document_path, list) else [],
        }
        for item in history
    ]