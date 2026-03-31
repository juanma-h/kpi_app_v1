from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, get_shift_service
from app.models.user import User
from app.schemas.shift import ShiftResponse, ShiftStartRequest
from app.services.shifts import ShiftService

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.post("/start", response_model=ShiftResponse)
def start_shift(
    payload: ShiftStartRequest,
    current_user: User = Depends(get_current_user),
    shift_service: ShiftService = Depends(get_shift_service),
) -> ShiftResponse:
    shift, session = shift_service.start_shift(
        user_id=current_user.id,
        device_label=payload.device_label,
    )

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )


@router.get("/current", response_model=ShiftResponse)
def current_shift(
    current_user: User = Depends(get_current_user),
    shift_service: ShiftService = Depends(get_shift_service),
) -> ShiftResponse:
    shift, session = shift_service.get_current_shift(user_id=current_user.id)

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )


@router.post("/end", response_model=ShiftResponse)
def end_shift(
    current_user: User = Depends(get_current_user),
    shift_service: ShiftService = Depends(get_shift_service),
) -> ShiftResponse:
    shift, session = shift_service.end_shift(user_id=current_user.id)

    return ShiftResponse(
        shift_id=shift.id,
        session_id=session.id,
        status=shift.status,
        start_at=shift.start_at,
        end_at=shift.end_at,
    )
