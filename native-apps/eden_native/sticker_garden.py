"""Garden Stars phase-2 sticker placement model. Staging only: no live UI changes."""
from __future__ import annotations

import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

# This manifest is installed atomically with the reviewed 75 transparent PNGs.
import json
_STICKER_MANIFEST_PATH=Path(__file__).resolve().parent.parent/"assets"/"stickers"/"manifest.json"
_STICKER_ITEMS=json.loads(_STICKER_MANIFEST_PATH.read_text(encoding="utf-8"))["items"]
STICKERS=frozenset(item["sku"] for item in _STICKER_ITEMS)
FREE_STICKERS=frozenset(item["sku"] for item in _STICKER_ITEMS if item["price"]==0)
MAX_PLACEMENTS = 40

class StickerGarden:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        if not Path(self.db_path).is_file():
            raise FileNotFoundError("Existing Garden Stars database required")
        with self._db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS sticker_placements (
                    id TEXT PRIMARY KEY,
                    profile_id TEXT NOT NULL REFERENCES profiles(id),
                    sku TEXT NOT NULL,
                    x REAL NOT NULL CHECK(x BETWEEN 0 AND 1),
                    y REAL NOT NULL CHECK(y BETWEEN 0 AND 1),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_sticker_child ON sticker_placements(profile_id)")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.db_path, timeout=10)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _position(x, y):
        if (not isinstance(x, (float, int)) or isinstance(x, bool)
                or not isinstance(y, (float, int)) or isinstance(y, bool)
                or not math.isfinite(x) or not math.isfinite(y)
                or not 0 <= x <= 1 or not 0 <= y <= 1):
            raise ValueError("Sticker position must be between 0 and 1")
        return float(x), float(y)

    @staticmethod
    def _owned(db, profile, sku):
        if sku in FREE_STICKERS:
            return True
        return db.execute(
            "SELECT 1 FROM inventory WHERE profile_id=? AND sku=?",
            (profile, sku)
        ).fetchone() is not None

    def list_placements(self, profile):
        with self._db() as db:
            rows = db.execute(
                "SELECT id,sku,x,y FROM sticker_placements WHERE profile_id=? ORDER BY created_at,id",
                (profile,)
            ).fetchall()
            # Historical placements remain in the DB for recovery, but old
            # sticker IDs must not appear in the replacement garden.
            return [dict(id=r[0], sku=r[1], x=r[2], y=r[3])
                    for r in rows if r[1] in STICKERS]

    def place(self, profile, sku, x, y):
        if sku not in STICKERS:
            raise ValueError("Not a sticker reward")
        x, y = self._position(x, y)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            if not self._owned(db, profile, sku):
                raise PermissionError("Sticker not unlocked for this child")
            # Old placements are retained in the DB for recovery, but do not
            # count toward the capacity of the replacement collection.
            existing_skus=db.execute(
                "SELECT sku FROM sticker_placements WHERE profile_id=?", (profile,)
            ).fetchall()
            count=sum(1 for row in existing_skus if row[0] in STICKERS)
            if count >= MAX_PLACEMENTS:
                raise ValueError("Sticker garden is full")
            occupied = db.execute(
                "SELECT sku FROM sticker_placements WHERE profile_id=? AND abs(x-?)<0.01 AND abs(y-?)<0.01",
                (profile, x, y)
            ).fetchone()
            if occupied and occupied[0] in STICKERS:
                raise ValueError("That garden space already has a sticker")
            placement_id = str(uuid4())
            db.execute(
                "INSERT INTO sticker_placements(id,profile_id,sku,x,y) VALUES (?,?,?,?,?)",
                (placement_id, profile, sku, x, y)
            )
            db.commit()
        return placement_id

    def move(self, profile, placement_id, x, y):
        x, y = self._position(x, y)
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            occupied = db.execute(
                "SELECT sku FROM sticker_placements WHERE profile_id=? AND id<>? AND abs(x-?)<0.01 AND abs(y-?)<0.01",
                (profile, placement_id, x, y)
            ).fetchone()
            if occupied and occupied[0] in STICKERS:
                raise ValueError("That garden space already has a sticker")
            result = db.execute(
                "UPDATE sticker_placements SET x=?,y=? WHERE id=? AND profile_id=?",
                (x, y, placement_id, profile)
            )
            if result.rowcount != 1:
                raise LookupError("Sticker placement not found for child")
            db.commit()

    def remove(self, profile, placement_id):
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            result = db.execute(
                "DELETE FROM sticker_placements WHERE id=? AND profile_id=?",
                (placement_id, profile)
            )
            if result.rowcount != 1:
                raise LookupError("Sticker placement not found for child")
            db.commit()
