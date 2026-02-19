import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from core.security import get_current_user
from database import get_db, supabase, BUCKET
from models.ot_record import OTRecord
from models.ot_details import OTDetail
from datetime import datetime
from typing import List
import uuid

router = APIRouter(prefix="/ot", tags=["OT"])

def generate_ref():
    return f"OT-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"




@router.post("/")
async def create_ot(
    ot_name: str = Form(...),
    status_id: int = Form(...),
    amount: str | None = Form(None),
    comments: str | None = Form(None),
    ot_date: str | None = Form(None),
    department_id: int = Form(...),

    # OPTIONAL FIELDS
    invoice_number: str | None = Form(None),
    files: List[UploadFile] | None = File(None),
    total_hours: str | None = Form(None),
    jira_id: str | None = Form(None),
    hr_ref_number: str | None = Form(None),
    project_manager: str | None = Form(None),
    activity_type:str | None = Form(None),
    rfc_number: str | None = Form(None),
    cost_center: str | None = Form(None),
    dates_worked: str | None = Form(None),
    document_names: str | None = Form(None),

    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ref = generate_ref()

    file_paths = []

    if files:
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
        updated_at=datetime.utcnow(),

        # NEW FIELDS
        total_hours=total_hours,
        jira_id=jira_id,
        hr_ref_number=hr_ref_number,
        project_manager=project_manager,
        activity_type=activity_type,
        rfc_number=rfc_number,
        cost_center=cost_center,
        dates_worked=json.loads(dates_worked) if dates_worked else [],
        document_names=json.loads(document_names) if document_names else [],
    )

    db.add(ot)
    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(ot)

    return {"reference_number": ref}


# ---------------------------------------------------------
# LIST OT (for table view)
# ---------------------------------------------------------
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
            "document_names": ot.document_names,
        })
    print(f"result: ${result}")
    return result


# ---------------------------------------------------------
# GET FULL OT DETAILS
# ---------------------------------------------------------
@router.get("/{reference_number}")
def get_ot_details(
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
        # NEW FIELDS
        "total_hours": ot.total_hours,
        "jira_id": ot.jira_id,
        "hr_ref_number": ot.hr_ref_number,
        "project_manager": ot.project_manager,
        "activity_type": ot.activity_type,
        "rfc_number": ot.rfc_number,
        "cost_center": ot.cost_center,
        "dates_worked": ot.dates_worked,
        "document_path": ot.document_path,
    }

@router.put("/{reference_number}")
async def update_ot_record(
    reference_number: str,
    ot_name: str = Form(...),
    status_id: int = Form(...),
    amount: str | None = Form(None),
    comments: str | None = Form(None),
    ot_date: str | None = Form(None),
    department_id: int = Form(...),

    invoice_number: str | None = Form(None),
    files: List[UploadFile] | None = File(None),

    total_hours: str | None = Form(None),
    jira_id: str | None = Form(None),
    hr_ref_number: str | None = Form(None),
    project_manager: str | None = Form(None),
    activity_type: str | None = Form(None),
    rfc_number: str | None = Form(None),
    cost_center: str | None = Form(None),
    dates_worked: str | None = Form(None),
    document_names: str | None = Form(None),

    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ot = db.query(OTRecord).filter(
        OTRecord.reference_number == reference_number,
        OTRecord.user_id == user["user_id"]
    ).first()

    if not ot:
        raise HTTPException(status_code=404, detail="OT Record not found")

    # -------------------------
    # Handle file uploads
    # -------------------------
    new_file_paths = []

    if files:
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

    ot.document_path = new_file_paths

    # -------------------------
    # Update fields
    # -------------------------
    ot.ot_name = ot_name
    ot.status_id = status_id
    ot.amount = amount
    ot.comments = comments
    ot.ot_date = ot_date
    ot.department_id = department_id
    ot.invoice_number = invoice_number
    ot.updated_at = datetime.utcnow()

    # NEW FIELDS
    ot.total_hours = total_hours
    ot.jira_id = jira_id
    ot.hr_ref_number = hr_ref_number
    ot.project_manager = project_manager
    ot.activity_type = activity_type
    ot.rfc_number = rfc_number
    ot.cost_center = cost_center
    ot.dates_worked = json.loads(dates_worked) if dates_worked else []
    ot.document_names = json.loads(document_names) if document_names else []

    try:
        db.commit()
    except:
        db.rollback()
        raise
    db.refresh(ot)

    return {"message": "OT updated", "document_path": ot.document_path}


# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------
@router.get("/{reference_number}/history")
def get_ot_history(
    reference_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(OTDetail).filter(
        OTDetail.reference_number == reference_number,
        OTDetail.user_id == user["user_id"]
    ).order_by(OTDetail.captured_at.desc()).all()

    if not history:
        return []

    result = []
    for h in history:
        result.append({
            "reference_number": h.reference_number,
            "ot_name": h.ot_name,
            "status_id": h.status_id,
            "amount": float(h.amount) if h.amount is not None else None,
            "comments": h.comments,
            "invoice_number": h.invoice_number,
            "ot_date": h.ot_date.isoformat() if h.ot_date else None,
            "department_id": h.department_id,
            "department_name": h.department_name if hasattr(h, "department_name") else None,
            "captured_at": h.captured_at.isoformat(),

            # NEW FIELDS
            "total_hours": h.total_hours,
            "jira_id": h.jira_id,
            "hr_ref_number": h.hr_ref_number,
            "project_manager": h.project_manager,
            "activity_type": h.activity_type,
            "rfc_number": h.rfc_number,
            "cost_center": h.cost_center,
            "dates_worked": h.dates_worked,
            "document_path": h.document_path,
        })

    return result

# ---------------------------------------------------------
# DELETE OT
# ---------------------------------------------------------
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