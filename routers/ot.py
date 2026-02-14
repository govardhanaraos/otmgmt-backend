from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db,supabase,BUCKET
from dictconverter.model2dict import model_to_dict
from models.ot_details import OTDetail
from schemas.ot import OTCreate, OTUpdate
from models.ot_record import OTRecord
from services.audit_service import log_audit
from fastapi import File, UploadFile, Form
import uuid
from datetime import datetime
from fastapi import Query
from typing import List


router = APIRouter(prefix="/ot", tags=["OT"])

def generate_ref():
    return f"OT-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"




@router.post("/")
async def create_ot(
    ot_name: str = Form(...),
    status_id: int = Form(...),
    amount: float = Form(...),
    comments: str = Form(None),
    ot_date: str = Form(...),
    department_id: int = Form(...),
    invoice_number: str = Form(None),
    files: List[UploadFile] = File([]),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ref = generate_ref()

    file_paths = []

    for file in files:
        file_bytes = await file.read()
        ext = file.filename.split(".")[-1]
        file_name = f"{ref}/{uuid.uuid4()}.{ext}"

        supabase.storage.from_(BUCKET).upload(
            file_name,
            file_bytes,
            file_options={"content-type": file.content_type}
        )

        file_paths.append(file_name)

    ot = OTRecord(
        reference_number=ref,
        user_id=user["user_id"],
        ot_name=ot_name,
        status_id=status_id,
        amount=amount,
        comments=comments,
        ot_date=ot_date,
        department_id=department_id,
        invoice_number=invoice_number,
        document_path=file_paths,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(ot)
    db.commit()
    db.refresh(ot)

    return {"reference_number": ref}


@router.get("/")
def list_ot(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
    search: str | None = Query(None),
    status_id: int | None = Query(None),
    department_id: int | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    amount_min: float | None = Query(None),
    amount_max: float | None = Query(None),
    invoice_number: str | None = Query(None),
    ref_umber: str | None = Query(None),
    created_from: str | None = Query(None),
    created_to: str | None = Query(None),
):

    print(f" params ${amount_min}")

    q = db.query(OTRecord).filter(OTRecord.user_id == user["user_id"])

    if search:
        q = q.filter(OTRecord.ot_name.ilike(f"%{search}%"))

    if status_id:
        q = q.filter(OTRecord.status_id == status_id)

    if department_id:
        q = q.filter(OTRecord.department_id == department_id)

    if date_from:
        q = q.filter(OTRecord.ot_date >= date_from)

    if date_to:
        q = q.filter(OTRecord.ot_date <= date_to)

    if amount_min:
        q = q.filter(OTRecord.amount >= amount_min)

    if amount_max:
        q = q.filter(OTRecord.amount <= amount_max)

    if created_from:
        q = q.filter(OTRecord.created_at >= created_from)

    if created_to:
        q = q.filter(OTRecord.created_at <= created_to)

    if invoice_number:
        q = q.filter(OTRecord.invoice_number.ilike(f"%{invoice_number}%"))
    if ref_umber:
        q = q.filter(OTRecord.reference_number.ilike(f"%{ref_umber}%"))

    q=q.filter(OTRecord.deleted != 'Y')
    ots = q.all()

    result = []
    for ot in ots:
        result.append({
            "reference_number": ot.reference_number,
            "ot_name": ot.ot_name,
            "status": ot.status.name,
            "status_id": ot.status_id,
            "amount": float(ot.amount),
            "ot_date": ot.ot_date.isoformat(),
            "department_id": ot.department_id,
            "department_name": ot.department.name if ot.department else None,
            "invoice_number": ot.invoice_number,
            "created_at": ot.created_at.strftime("%d/%m/%Y %H:%M:%S") if ot.created_at else None,
            "updated_at": ot.updated_at.strftime("%d/%m/%Y %H:%M:%S") if ot.updated_at else None,
        })
    print(f"result: ${result}")
    return result


@router.get("/{reference_number}")
def get_ot_details(
    reference_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Query for the specific OT record belonging to the user
    ot = db.query(OTRecord).filter(
        OTRecord.reference_number == reference_number,
        OTRecord.user_id == user["user_id"]
    ).first()

    # If not found, return 404
    if not ot:
        raise HTTPException(status_code=404, detail="OT record not found")

    # Return the detailed object
    return {
        "reference_number": ot.reference_number,
        "ot_name": ot.ot_name,
        "status": ot.status.name,
        "status_id": ot.status_id,
        "amount": float(ot.amount),
        "ot_date": ot.ot_date.isoformat(),
        "department_id": ot.department_id,
        "department_name": ot.department.name if ot.department else None,
        "invoice_number": ot.invoice_number,
        "comments": ot.comments,  # Included comments for the detail view
        "created_at": ot.created_at.isoformat() if ot.created_at else None,
        "updated_at": ot.updated_at.isoformat() if ot.updated_at else None,
    }

@router.put("/{reference_number}")
async def update_ot_record(
    reference_number: str,
    ot_name: str = Form(...),
    status_id: int = Form(...),
    amount: float = Form(...),
    comments: str = Form(None),
    ot_date: str = Form(...),
    department_id: int = Form(...),
    invoice_number: str = Form(None),
    files: List[UploadFile] = File([]), # Updated to List
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ot = db.query(OTRecord).filter(
        OTRecord.reference_number == reference_number,
        OTRecord.user_id == user["user_id"]
    ).first()

    if not ot:
        raise HTTPException(status_code=404, detail="OT Record not found")

    # Handle multiple file uploads
    new_file_paths = []
    for file in files:
        file_bytes = await file.read()
        ext = file.filename.split(".")[-1]
        file_name = f"{reference_number}/{uuid.uuid4()}.{ext}"

        supabase.storage.from_(BUCKET).upload(
            file_name,
            file_bytes,
            file_options={"content-type": file.content_type}
        )
        new_file_paths.append(file_name)

    # Append new files to existing ones if any
    if new_file_paths:
        existing_files = ot.document_path if ot.document_path else []
        if isinstance(existing_files, list):
            ot.document_path = existing_files + new_file_paths
        else:
            ot.document_path = new_file_paths

    # Update other fields
    ot.ot_name = ot_name
    ot.status_id = status_id
    ot.amount = amount
    ot.comments = comments
    ot.ot_date = ot_date
    ot.department_id = department_id
    ot.invoice_number = invoice_number
    ot.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ot)

    return {"message": "OT updated", "document_path": ot.document_path}

@router.get("/{reference_number}/history")
def get_ot_history(
    reference_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Query the details table (the audit log)
    # We still check user_id to ensure they own the record they are viewing
    history = db.query(OTDetail).filter(
        OTDetail.reference_number == reference_number,
        OTDetail.user_id == user["user_id"]
    ).order_by(OTDetail.captured_at.desc()).all()

    if not history:
        # If the master record exists but no history does (unlikely with our trigger),
        # we return an empty list or 404.
        return []

    return [
        {
            "id": str(h.id),
            "ot_name": h.ot_name,
            "status_id": h.status_id,
            "amount": float(h.amount),
            "comments": h.comments,
            "invoice_number": h.invoice_number,
            "captured_at": h.captured_at.isoformat(),
            "department_id": h.department_id
        }
        for h in history
    ]


@router.delete("/{reference_number}")
def delete_ot(
        reference_number: str,
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    ot = db.query(OTRecord).filter(
        OTRecord.reference_number == reference_number,
        OTRecord.user_id == user["user_id"]
    ).first()

    if not ot:
        raise HTTPException(status_code=404, detail="OT record not found")

    # Soft delete: Update the flag instead of deleting the row
    ot.deleted = 'Y'
    ot.updated_at = datetime.utcnow()

    db.commit()
    return {"message": "OT record marked as deleted"}