from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.repositories.part_repository import PartRepository
from app.models.models import Part, PartType
from app.utils.id_generator import generate_part_id

class PartService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PartRepository(db)

    def create_part(self, name: str, type_: PartType, components: List[Dict] = None) -> Part:
        existing = self.repo.get_by_name(name)
        if existing:
            raise ValueError("Part with this name already exists")

        part_id = generate_part_id(name)
        part = Part(id=part_id, name=name, type=type_, quantity=0)
        self.repo.create(part)

        if type_ == PartType.ASSEMBLED:
            comp_list: List[Tuple[str, int]] = []
            for c in components:
                comp_part = self.repo.get_by_id(c["id"])
                if not comp_part:
                    raise ValueError(f"Component not found: {c['id']}")
                if comp_part.id == part.id:
                    raise ValueError("Part cannot include itself")
                comp_list.append((comp_part.id, c["quantity"]))

            for comp_id, _ in comp_list:
                if self._dependency_contains(comp_id, part.id):
                    raise ValueError(f"Adding component {comp_id} would create a circular dependency")

            self.repo.set_components(part.id, comp_list)

        self.db.commit()
        return part

    def _dependency_contains(self, start_id: str, search_id: str, visited=None) -> bool:
        if visited is None:
            visited = set()
        if start_id in visited:
            return False
        visited.add(start_id)
        comps = self.repo.get_components(start_id)
        for c in comps:
            if c["id"] == search_id:
                return True
            if self._dependency_contains(c["id"], search_id, visited):
                return True
        return False

    def list_parts(self):
        return self.repo.list_parts()

    def get_part(self, part_id: str):
        return self.repo.get_by_id(part_id)

    def get_components(self, part_id: str):
        return self.repo.get_components(part_id)