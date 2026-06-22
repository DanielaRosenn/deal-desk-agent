import json
import os
import random
from pathlib import Path
from typing import Any

from agent.schemas import Approver

# Persona drives card layout/limits; role drives routing-rule matching.
_ROLE_PROFILES: dict[str, dict] = {
    "manager": {"persona": "manager", "title": "Regional Sales Manager"},
    "director": {"persona": "director", "title": "Sales Director"},
    "vp_sales": {"persona": "vp", "title": "VP of Sales"},
    "cfo": {"persona": "cfo", "title": "Chief Financial Officer"},
    "cro": {"persona": "cfo", "title": "Chief Revenue Officer"},
    "legal": {"persona": "legal", "title": "Legal Counsel"},
}

# Pool of plausible approver names used for the demo (real identities come from
# HiBob in production - see HiBobManagerResolver below).
_NAME_POOL = [
    "Jordan Avery", "Morgan Blake", "Riley Chen", "Casey Diaz", "Taylor Ellis",
    "Jamie Fox", "Alex Grant", "Sydney Hale", "Drew Iqbal", "Quinn Lopez",
]


class MockManagerResolver:
    """Resolves the approver for a given role for the demo.

    Every approval is delivered to a single real mailbox (``DEMO_APPROVER_EMAIL``)
    so the live Outlook test reaches an inbox we control, while each tier gets a
    realistic (randomly assigned, stable-per-instance) name and title.
    """

    def __init__(self, demo_email: str, seed: int | None = None):
        self._demo_email = demo_email
        self._rng = random.Random(seed)
        self._names = self._rng.sample(_NAME_POOL, k=len(_NAME_POOL))
        self._assigned: dict[str, str] = {}

    def _name_for(self, role: str) -> str:
        if role not in self._assigned:
            idx = len(self._assigned) % len(self._names)
            self._assigned[role] = self._names[idx]
        return self._assigned[role]

    def resolve_approver_for_role(self, role: str) -> Approver:
        profile = _ROLE_PROFILES.get(role, _ROLE_PROFILES["manager"])
        name = self._name_for(role)
        return Approver(
            user_id=f"user-{role}",
            email=self._demo_email,
            persona=profile["persona"],
            role=role,
            display_name=f"{name} ({profile['title']})",
        )

    def resolve_management_chain(self, roles: list[str], owner_email: str = "") -> list[Approver]:
        chain: list[Approver] = []
        seen: set[str] = set()
        for role in roles:
            if role in seen:
                continue
            seen.add(role)
            chain.append(self.resolve_approver_for_role(role))
        return chain


class HiBobManagerResolver:
    """HiBob-like manager resolution from a local org JSON.

    This resolver mimics HiBob org traversal without calling external APIs.
    It walks `reportsTo` links from the opportunity owner up the management
    hierarchy and resolves required roles in order.
    """

    def __init__(self, demo_email: str):
        self._fallback = MockManagerResolver(demo_email)
        self._demo_email = demo_email
        base_dir = Path(__file__).resolve().parent.parent
        default_path = base_dir / "configs" / "hibob_org.json"
        configured = os.getenv("HIBOB_MOCK_FILE", "").strip()
        self._org_path = Path(configured) if configured else default_path
        self._employees: dict[str, dict[str, Any]] = {}
        self._email_to_id: dict[str, str] = {}
        self._default_owner_email = ""
        self._load_org()

    def _load_org(self) -> None:
        try:
            data = json.loads(self._org_path.read_text(encoding="utf-8"))
            rows = data.get("employees") if isinstance(data, dict) else None
            if not isinstance(rows, list):
                return
            for item in rows:
                if not isinstance(item, dict):
                    continue
                emp_id = str(item.get("id") or "").strip()
                if not emp_id:
                    continue
                self._employees[emp_id] = item
                email = str(item.get("email") or "").strip().lower()
                if email:
                    self._email_to_id[email] = emp_id
            self._default_owner_email = str(data.get("defaultOwnerEmail") or "").strip().lower()
        except Exception:
            self._employees = {}
            self._email_to_id = {}
            self._default_owner_email = ""

    def _can_read_org(self) -> bool:
        return bool(self._employees)

    @staticmethod
    def _infer_role(title: str, explicit_role: str = "") -> str:
        if explicit_role:
            role = explicit_role.strip().lower()
            if role in _ROLE_PROFILES:
                return role
        t = (title or "").lower()
        if "chief revenue officer" in t or t == "cro":
            return "cro"
        if "chief financial officer" in t or t == "cfo" or "finance" in t and "chief" in t:
            return "cfo"
        if "vp" in t and "sales" in t:
            return "vp_sales"
        if "director" in t:
            return "director"
        if "manager" in t:
            return "manager"
        return "manager"

    def _resolve_owner_id(self, owner_email: str = "") -> str:
        email = owner_email.strip().lower()
        if email and email in self._email_to_id:
            return self._email_to_id[email]
        if self._default_owner_email and self._default_owner_email in self._email_to_id:
            return self._email_to_id[self._default_owner_email]
        if self._employees:
            return next(iter(self._employees.keys()))
        return ""

    def _walk_chain(self, required_roles: list[str], owner_email: str = "") -> list[Approver]:
        current_id = self._resolve_owner_id(owner_email)
        role_to_person: dict[str, dict[str, Any]] = {}
        max_hops = 12
        hops = 0
        while current_id and hops < max_hops and len(role_to_person) < len(set(required_roles)):
            hops += 1
            person = self._employees.get(current_id) or {}
            title = str(person.get("title") or "")
            explicit_role = str(person.get("role") or "")
            role = self._infer_role(title, explicit_role)
            role_to_person.setdefault(role, person)
            current_id = str(person.get("reportsTo") or "").strip()

        chain: list[Approver] = []
        for role in required_roles:
            person = role_to_person.get(role)
            if not person:
                chain.append(self._fallback.resolve_approver_for_role(role))
                continue
            profile = _ROLE_PROFILES.get(role, _ROLE_PROFILES["manager"])
            chain.append(
                Approver(
                    user_id=str(person.get("id") or f"user-{role}"),
                    email=str(person.get("email") or self._demo_email),
                    persona=profile["persona"],
                    role=role,
                    display_name=f"{person.get('display_name') or profile['title']} ({profile['title']})",
                )
            )
        return chain

    def resolve_approver_for_role(self, role: str) -> Approver:
        return self.resolve_management_chain([role])[0]

    def resolve_management_chain(self, roles: list[str], owner_email: str = "") -> list[Approver]:
        unique_roles: list[str] = []
        seen: set[str] = set()
        for role in roles:
            if role in seen:
                continue
            seen.add(role)
            unique_roles.append(role)
        if not unique_roles:
            unique_roles = ["manager"]

        if not self._can_read_org():
            return self._fallback.resolve_management_chain(unique_roles)

        return self._walk_chain(unique_roles, owner_email=owner_email)


def build_manager_resolver(settings):
    demo_email = os.getenv("DEMO_APPROVER_EMAIL", "daniela.rosenstein@catonetworks.com")
    if getattr(settings, "manager_resolver", "mock") == "hibob":
        return HiBobManagerResolver(demo_email)
    return MockManagerResolver(demo_email)
