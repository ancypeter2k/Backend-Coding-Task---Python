from sqlalchemy.orm import Session
from app.models.models import Part, assembly_parts, PartType, User, AuditLog
from typing import List, Dict, Tuple

class PartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, part_id: str) -> Part:
        return self.db.query(Part).filter(Part.id == part_id).first()

    def get_by_name(self, name: str) -> Part:
        return self.db.query(Part).filter(Part.name == name).first()

    def create(self, part: Part):
        self.db.add(part)
        self.db.flush()
        return part

    def set_components(self, assembly_id: str, components: List[Tuple[str, int]]):
        # delete existing entries for assembly_id
        self.db.execute(
            assembly_parts.delete().where(assembly_parts.c.assembly_id == assembly_id)
        )
        for comp_id, qty in components:
            self.db.execute(
                assembly_parts.insert().values(assembly_id=assembly_id, component_id=comp_id, quantity=qty)
            )

    def get_components(self, assembly_id: str) -> List[Dict]:
        rows = self.db.execute(
            assembly_parts.select().where(assembly_parts.c.assembly_id == assembly_id)
        ).mappings().all()
        return [{"id": r["component_id"], "quantity": r["quantity"]} for r in rows]

    def increment_quantity(self, part_id: str, delta: int):
        part = self.get_by_id(part_id)
        if not part:
            raise ValueError("Part not found")
        part.quantity += delta
        self.db.add(part)

    def list_parts(self):
        return self.db.query(Part).all()

    def create_audit(self, user_id: int, action: str, detail: str = None):
        log = AuditLog(user_id=user_id, action=action, detail=detail)
        self.db.add(log)