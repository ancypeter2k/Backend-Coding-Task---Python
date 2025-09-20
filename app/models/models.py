import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.database import Base

class PartType(str, enum.Enum):
    RAW = "RAW"
    ASSEMBLED = "ASSEMBLED"

# association table with quantity attribute
assembly_parts = Table(
    "assembly_parts",
    Base.metadata,
    Column("assembly_id", String, ForeignKey("parts.id"), primary_key=True),
    Column("component_id", String, ForeignKey("parts.id"), primary_key=True),
    Column("quantity", Integer, nullable=False),
)

class Part(Base):
    __tablename__ = "parts"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(Enum(PartType), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    # relationship is useful for eager loads, but quantities are read via assembly_parts queries
    components = relationship(
        "Part",
        secondary=assembly_parts,
        primaryjoin=id == assembly_parts.c.assembly_id,
        secondaryjoin=id == assembly_parts.c.component_id,
        viewonly=True,
    )

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Creator or Viewer

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    detail = Column(String, nullable=True)