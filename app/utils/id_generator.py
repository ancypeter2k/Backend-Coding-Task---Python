from slugify import slugify
import uuid

def generate_part_id(name: str) -> str:
    base = slugify(name)[:40]
    short = uuid.uuid4().hex[:6]
    return f"{base}-{short}"