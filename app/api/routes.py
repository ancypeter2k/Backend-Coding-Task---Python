from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schemas import CreatePartRequest, CreatePartResponse, AddInventoryRequest, AddInventoryResponse, TokenRequest, TokenResponse
from app.api.deps import get_db_session, get_current_user, require_role
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.services.part_service import PartService
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api")

@router.post("/auth/token", response_model=TokenResponse)
def login(payload: TokenRequest, db: Session = Depends(get_db_session)):
    svc = AuthService(db)
    user = svc.authenticate(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return svc.create_token(user)

@router.post("/part", response_model=CreatePartResponse)
def create_part(request: CreatePartRequest, user=Depends(require_role("Creator")), db: Session = Depends(get_db_session)):
    service = PartService(db)
    try:
        comps = [c.dict() for c in request.parts] if request.parts else None
        part = service.create_part(request.name, request.type, comps)
        response = {
            "id": part.id,
            "name": part.name,
            "type": part.type.value,
            "parts": comps if comps else None
        }
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/part/{part_id}", response_model=AddInventoryResponse)
def add_inventory(part_id: str, payload: AddInventoryRequest, user=Depends(require_role("Creator")), db: Session = Depends(get_db_session)):
    inv = InventoryService(db)
    result = inv.add_inventory(part_id, payload.quantity, user.id)
    if result.get("status") == "SUCCESS":
        return {"status": "SUCCESS"}
    raise HTTPException(status_code=400, detail=result.get("message"))

@router.get("/parts")
def list_parts(user=Depends(get_current_user), db: Session = Depends(get_db_session)):
    service = PartService(db)
    parts = service.list_parts()
    out = []
    for p in parts:
        comps = service.get_components(p.id)
        out.append({
            "id": p.id,
            "name": p.name,
            "type": p.type.value,
            "quantity": p.quantity,
            "parts": comps if comps else None
        })
    return out