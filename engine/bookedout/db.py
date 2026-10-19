"""SQLite storage for leads and their outreach history."""

import sqlite3
from datetime import datetime, timezone

from .models import LEAD_FIELDS, LEAD_TYPES, Lead, is_empty


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sql_type(py_type) -> str:
    text = str(py_type)
    if "float" in text:
        return "REAL"
    if "int" in text:
        return "INTEGER"
    return "TEXT"


class LeadStore:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        cols = ", ".join(
            f"{name} {_sql_type(LEAD_TYPES[name])}" + (" PRIMARY KEY" if name == "id" else "")
            for name in LEAD_FIELDS
        )
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS leads ({cols})")
        # Add columns introduced after the database was created.
        existing = {row["name"] for row in self.conn.execute("PRAGMA table_info(leads)")}
        for name in LEAD_FIELDS:
            if name not in existing:
                self.conn.execute(f"ALTER TABLE leads ADD COLUMN {name} {_sql_type(LEAD_TYPES[name])}")
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT, at TEXT, kind TEXT, detail TEXT)"
        )
        for col in ("domain", "phone", "email"):
            self.conn.execute(f"CREATE INDEX IF NOT EXISTS idx_leads_{col} ON leads({col})")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # --- reads -----------------------------------------------------------

    def _row_to_lead(self, row: sqlite3.Row) -> Lead:
        return Lead(**{name: row[name] for name in LEAD_FIELDS})

    def get(self, lead_id: str) -> Lead | None:
        row = self.conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        return self._row_to_lead(row) if row else None

    def find(self, key: str) -> Lead | None:
        """Look a lead up by id, domain, email or phone (digits only is fine)."""
        key = key.strip()
        lead = self.get(key)
        if lead:
            return lead
        lowered = key.lower().removeprefix("https://").removeprefix("http://").removeprefix("www.").rstrip("/")
        for col, value in (("domain", lowered), ("email", lowered)):
            row = self.conn.execute(f"SELECT * FROM leads WHERE {col} = ?", (value,)).fetchone()
            if row:
                return self._row_to_lead(row)
        digits = "".join(ch for ch in key if ch.isdigit())
        if len(digits) >= 10:
            row = self.conn.execute("SELECT * FROM leads WHERE phone LIKE ?", (f"%{digits[-10:]}",)).fetchone()
            if row:
                return self._row_to_lead(row)
        return None

    def all(self, where: str = "", params: tuple = ()) -> list[Lead]:
        sql = "SELECT * FROM leads" + (f" WHERE {where}" if where else "")
        return [self._row_to_lead(row) for row in self.conn.execute(sql, params)]

    def events(self, lead_id: str | None = None, kind: str | None = None) -> list[sqlite3.Row]:
        clauses, params = [], []
        if lead_id:
            clauses.append("lead_id = ?")
            params.append(lead_id)
        if kind:
            clauses.append("kind = ?")
            params.append(kind)
        sql = "SELECT * FROM events" + (" WHERE " + " AND ".join(clauses) if clauses else "") + " ORDER BY id"
        return list(self.conn.execute(sql, params))

    # --- writes ----------------------------------------------------------

    def save(self, lead: Lead, commit: bool = True) -> None:
        lead.updated_at = now_iso()
        if not lead.created_at:
            lead.created_at = lead.updated_at
        placeholders = ", ".join("?" for _ in LEAD_FIELDS)
        self.conn.execute(
            f"INSERT OR REPLACE INTO leads ({', '.join(LEAD_FIELDS)}) VALUES ({placeholders})",
            [getattr(lead, name) for name in LEAD_FIELDS],
        )
        if commit:
            self.conn.commit()

    def _match_existing(self, lead: Lead) -> Lead | None:
        existing = self.get(lead.id)
        if existing:
            return existing
        if lead.domain:
            row = self.conn.execute("SELECT * FROM leads WHERE domain = ?", (lead.domain,)).fetchone()
            if row:
                return self._row_to_lead(row)
        if lead.phone:
            row = self.conn.execute("SELECT * FROM leads WHERE phone = ?", (lead.phone,)).fetchone()
            if row:
                return self._row_to_lead(row)
        return None

    def upsert(self, lead: Lead, commit: bool = True) -> tuple[Lead, bool]:
        """Insert a lead, or fill the blanks of the matching existing lead.

        Existing non-empty values are never overwritten, so re-importing a list
        (or importing an Apollo contact export on top of a Google Maps list)
        only adds information.
        """
        existing = self._match_existing(lead)
        if existing is None:
            self.save(lead, commit=commit)
            return lead, True
        for name in LEAD_FIELDS:
            if name in ("id", "created_at", "updated_at", "status"):
                continue
            if is_empty(getattr(existing, name)) and not is_empty(getattr(lead, name)):
                setattr(existing, name, getattr(lead, name))
        self.save(existing, commit=commit)
        return existing, False

    def log(self, lead_id: str, kind: str, detail: str = "", commit: bool = True) -> None:
        self.conn.execute(
            "INSERT INTO events (lead_id, at, kind, detail) VALUES (?, ?, ?, ?)",
            (lead_id, now_iso(), kind, detail),
        )
        if commit:
            self.conn.commit()

    def commit(self) -> None:
        self.conn.commit()
