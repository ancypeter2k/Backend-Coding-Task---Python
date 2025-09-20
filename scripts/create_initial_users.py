import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, Base, engine
from app.models.models import User
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    # Force reset creator user
    creator = db.query(User).filter(User.username == "creator").first()
    if creator:
        creator.password_hash = hash_password("creatorpass")
        creator.role = "creator"
    else:
        creator = User(
            username="creator",
            password_hash=hash_password("creatorpass"),
            role="creator"
        )
        db.add(creator)

    # Force reset viewer user
    viewer = db.query(User).filter(User.username == "viewer").first()
    if viewer:
        viewer.password_hash = hash_password("viewerpass")
        viewer.role = "viewer"
    else:
        viewer = User(
            username="viewer",
            password_hash=hash_password("viewerpass"),
            role="viewer"
        )
        db.add(viewer)

    db.commit()
    print("✅ Users reset: creator/creatorpass and viewer/viewerpass")
finally:
    db.close()
