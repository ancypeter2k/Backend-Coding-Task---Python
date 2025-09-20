from sqlalchemy.orm import Session
from typing import Dict
from app.repositories.part_repository import PartRepository
from app.models.models import PartType
from collections import defaultdict

class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PartRepository(db)

    def add_inventory(self, part_id: str, quantity: int, acting_user_id: int) -> Dict:
        part = self.repo.get_by_id(part_id)
        if not part:
            return {"status": "FAILED", "message": "Part not found"}

        if quantity <= 0:
            return {"status": "FAILED", "message": "Quantity must be > 0"}

        if part.type == PartType.RAW:
            try:
                self.repo.increment_quantity(part_id, quantity)
                self.repo.create_audit(acting_user_id, "ADD_INVENTORY_RAW", f"{part_id}:{quantity}")
                self.db.commit()
                return {"status": "SUCCESS"}
            except Exception as e:
                self.db.rollback()
                return {"status": "FAILED", "message": str(e)}

        # ASSEMBLED part. Expand to required raw components (leaf parts)
        required = self._compute_requirements(part_id, quantity)
        insufficient = []
        for pid, req_qty in required.items():
            p = self.repo.get_by_id(pid)
            if not p:
                return {"status": "FAILED", "message": f"Component missing: {pid}"}
            if p.quantity < req_qty:
                insufficient.append((pid, req_qty, p.quantity))
        if insufficient:
            pid, needed, available = insufficient[0]
            return {"status": "FAILED", "message": f"Insufficient quantity - {pid} (needed {needed}, available {available})"}

        # Deduct and increment assembled quantity atomically
        try:
            for pid, req_qty in required.items():
                self.repo.increment_quantity(pid, -req_qty)
            self.repo.increment_quantity(part_id, quantity)
            self.repo.create_audit(acting_user_id, "ADD_INVENTORY_ASSEMBLED", f"{part_id}:{quantity}")
            self.db.commit()
            return {"status": "SUCCESS"}
        except Exception as e:
            self.db.rollback()
            return {"status": "FAILED", "message": str(e)}

    def _compute_requirements(self, part_id: str, multiplier: int) -> Dict[str, int]:
        """
        Recursively expand an assembled part into counts of leaf components.
        Leaves are parts that have no components defined in assembly_parts.
        """
        requirements = defaultdict(int)

        def dfs(pid: str, count: int, visited=None):
            if visited is None:
                visited = set()
            if pid in visited:
                raise ValueError("Detected circular dependency during expansion")
            visited.add(pid)
            comps = self.repo.get_components(pid)
            if not comps:
                requirements[pid] += count
                return
            for c in comps:
                dfs(c["id"], count * c["quantity"], visited.copy())

        dfs(part_id, multiplier)
        return dict(requirements)