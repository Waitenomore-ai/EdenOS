"""Garden Stars domain engine (staging only). No web endpoints or child PII stored here."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ACTIVITIES = {
    "number_meadow": 10, "word_woodland": 10, "puzzle_pond": 10,
    "story_garden": 10, "art_studio": 10, "nature_explorer": 5,
}
# The v70 replacement has exactly 75 sticker rewards.
# Historical wallpaper/garden purchases remain in the child database for recovery.
CATALOGUE = {}

# Only the new sticker collection is offered; legacy earned inventory and
# ledger entries are left untouched to preserve children's balances/history.
# This manifest is installed atomically with the reviewed 75 transparent PNGs.
import json
_STICKER_MANIFEST_PATH=Path(__file__).resolve().parent.parent/"assets"/"stickers"/"manifest.json"
_STICKER_ITEMS=json.loads(_STICKER_MANIFEST_PATH.read_text(encoding="utf-8"))["items"]
CATALOGUE.update({item["sku"]:("sticker",item["price"],1) for item in _STICKER_ITEMS})

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS profiles (id TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS events (
 id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id),
 activity TEXT NOT NULL, stars INTEGER NOT NULL CHECK(stars >= 0),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS ledger (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 profile_id TEXT NOT NULL REFERENCES profiles(id),
 delta INTEGER NOT NULL, reason TEXT NOT NULL, reference TEXT NOT NULL UNIQUE,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS inventory (
 profile_id TEXT NOT NULL REFERENCES profiles(id), sku TEXT NOT NULL,
 unlock_type TEXT NOT NULL CHECK(unlock_type IN ('earned','parent')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(profile_id,sku)
);
"""
class GardenStars:
    def __init__(self, db_path):
        self.db_path=str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db: db.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        db=sqlite3.connect(self.db_path,timeout=10,isolation_level=None)
        try:
            db.execute("PRAGMA foreign_keys=ON")
            yield db
        finally:
            db.close()

    @staticmethod
    def _balance(db, profile):
        return db.execute("SELECT COALESCE(SUM(delta),0) FROM ledger WHERE profile_id=?", (profile,)).fetchone()[0]

    def create_profile(self, profile):
        if not profile or not isinstance(profile,str): raise ValueError("Invalid profile ID")
        with self._connect() as db: db.execute("INSERT OR IGNORE INTO profiles(id) VALUES (?)",(profile,))

    def balance(self, profile):
        with self._connect() as db: return self._balance(db,profile)

    def earn(self, profile, activity, event_id):
        if activity not in ACTIVITIES: raise ValueError("Unknown rewardable activity")
        if not isinstance(event_id,str) or not 8<=len(event_id)<=128: raise ValueError("Invalid unique event ID")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT profile_id,activity,stars FROM events WHERE id=?",(event_id,)).fetchone()
            if existing:
                if existing[0]!=profile or existing[1]!=activity: raise ValueError("Conflicting event ID")
                db.commit()
                return {"awarded":0,"balance":self._balance(db,profile),"duplicate":True}
            points=ACTIVITIES[activity]
            # Limit awards, not play. Daily cap per activity avoids repetitive farming.
            earned_today=db.execute(
                "SELECT COALESCE(SUM(stars),0) FROM events "
                "WHERE profile_id=? AND activity=? AND date(created_at)=date('now')",
                (profile,activity)
            ).fetchone()[0]
            if earned_today+points>100:
                db.commit()
                return {"awarded":0,"balance":self._balance(db,profile),"daily_limit":True}
            db.execute("INSERT INTO events(id,profile_id,activity,stars) VALUES(?,?,?,?)",(event_id,profile,activity,points))
            db.execute("INSERT INTO ledger(profile_id,delta,reason,reference) VALUES(?,?,?,?)",
                       (profile,points,"activity:"+activity,"earn:"+event_id))
            new_balance=self._balance(db,profile)
            db.commit()
            return {"awarded":points,"balance":new_balance,"duplicate":False}

    def unlock(self, profile, sku, *, parent_authorized=False, release_phase=1):
        if sku not in CATALOGUE: raise ValueError("Unknown reward")
        kind, price, phase=CATALOGUE[sku]
        if phase>release_phase: raise ValueError("Reward is not released yet")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT unlock_type FROM inventory WHERE profile_id=? AND sku=?",(profile,sku)).fetchone()
            if existing:
                db.commit()
                return {"owned":True,"spent":0,"source":existing[0],"balance":self._balance(db,profile)}
            if not parent_authorized and self._balance(db,profile)<price: raise ValueError("Not enough stars")
            if not parent_authorized:
                db.execute("INSERT INTO ledger(profile_id,delta,reason,reference) VALUES(?,?,?,?)",
                           (profile,-price,"reward:"+sku,"buy:"+profile+":"+sku))
            source="parent" if parent_authorized else "earned"
            db.execute("INSERT INTO inventory(profile_id,sku,unlock_type) VALUES(?,?,?)",(profile,sku,source))
            balance=self._balance(db,profile)
            db.commit()
            return {"owned":True,"spent":0 if parent_authorized else price,"source":source,"balance":balance}

    def collection(self, profile):
        with self._connect() as db:
            return [{"sku":r[0],"source":r[1]} for r in db.execute(
                "SELECT sku,unlock_type FROM inventory WHERE profile_id=? ORDER BY created_at,sku",(profile,))]
