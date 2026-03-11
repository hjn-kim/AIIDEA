import json
import sys
import uuid
from datetime import datetime
from pathlib import Path


def _get_db_path() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent.parent
    db_dir = base / "aiidea_data"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "documents.json"


class DocumentDB:
    _documents: list[dict] = []
    _loaded: bool = False

    @classmethod
    def _load(cls):
        if cls._loaded:
            return
        path = _get_db_path()
        if path.exists():
            try:
                cls._documents = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                cls._documents = []
        cls._loaded = True

    @classmethod
    def _save(cls):
        _get_db_path().write_text(
            json.dumps(cls._documents, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    @classmethod
    def get_all(cls) -> list[dict]:
        cls._load()
        return cls._documents

    @classmethod
    def add(cls, name: str, content: str) -> dict:
        cls._load()
        doc = {
            "id": str(uuid.uuid4()),
            "name": name,
            "content": content,
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        cls._documents.append(doc)
        cls._save()
        return doc

    @classmethod
    def remove(cls, doc_id: str):
        cls._load()
        cls._documents = [d for d in cls._documents if d["id"] != doc_id]
        cls._save()

    @classmethod
    def get_context_text(cls) -> str:
        """AI 프롬프트에 포함할 참고 자료 텍스트 반환"""
        cls._load()
        if not cls._documents:
            return ""
        parts = [f"[참고자료: {doc['name']}]\n{doc['content']}" for doc in cls._documents]
        return "\n\n---\n\n".join(parts)
