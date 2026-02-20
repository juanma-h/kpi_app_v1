from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.shift import Shift
from app.models.session import Session as WorkSession
from app.models.user import User
from app.schemas.shift import ShiftStartRequest, ShiftResponse

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.post("/start", response_model=ShiftResponse)
def start_shift(
    payload: ShiftStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShiftResponse:
    # 1) Validar que no exista shift OPEN
    existing_shift = (
        db.query(Shift)
        .filter(Shift.user_id == current_user.id, Shift.status == "OPEN")
        .first()
    )
    if existing_shift:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un turno abierto para este usuario.",
        )

    now = datetime.now(timezone.utc)

    # 2) Crear shift OPEN
    shift = Shift(user_id=current_user.id, start_at=now, status="OPEN")
    db.add(shift)
    db.flush()  # para obtener shift.id sin commit todavía

    # 3) Crear session OPEN asociada
    session = WorkSession(
        user_id=current_user.id,
        shift_id=shift.id,
        start_at=now,
        status="OPEN",
        device_label=payload.device_label,
    )
    db.add(session)
    db.commit()
    db.refresh(shift)
    db.refresh(session)

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )


@router.get("/current", response_model=ShiftResponse)
def current_shift(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShiftResponse:
    shift = (
        db.query(Shift)
        .filter(Shift.user_id == current_user.id, Shift.status == "OPEN")
        .first()
    )
    if not shift:
        raise HTTPException(status_code=404, detail="No hay turno abierto.")

    session = (
        db.query(WorkSession)
        .filter(WorkSession.shift_id == shift.id, WorkSession.status == "OPEN")
        .first()
    )
    if not session:
        # Esto no debería pasar, pero lo manejamos
        raise HTTPException(status_code=500, detail="Turno abierto sin sesión activa.")

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )


@router.post("/end", response_model=ShiftResponse)
def end_shift(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShiftResponse:
    shift = (
        db.query(Shift)
        .filter(Shift.user_id == current_user.id, Shift.status == "OPEN")
        .first()
    )
    if not shift:
        raise HTTPException(status_code=404, detail="No hay turno abierto.")

    session = (
        db.query(WorkSession)
        .filter(WorkSession.shift_id == shift.id, WorkSession.status == "OPEN")
        .first()
    )
    if not session:
        raise HTTPException(status_code=500, detail="Turno abierto sin sesión activa.")

    now = datetime.now(timezone.utc)

    # Cerrar ambos
    shift.status = "CLOSED"
    shift.end_at = now
    session.status = "CLOSED"
    session.end_at = now

    db.commit()
    db.refresh(shift)
    db.refresh(session)

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )
