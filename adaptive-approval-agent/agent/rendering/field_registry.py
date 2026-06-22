import json
import logging
import re
from pathlib import Path
from typing import Any

from agent.schemas import FieldDefinition, FieldRegistryDoc, FieldRegistryError
from agent.schemas.card import _FIELD_ID_RE

LOG = logging.getLogger(__name__)


class FieldRegistry:
    def __init__(self, doc: FieldRegistryDoc):
        self.doc = doc
        self.process_type = doc.process_type
        self.version = doc.version
        self._fields = doc.fields
        self._personas = doc.personas

    @classmethod
    def from_file(cls, path: Path) -> "FieldRegistry":
        try:
            doc = FieldRegistryDoc.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            raise FieldRegistryError(f"Failed to load registry from {path}: {exc}") from exc
        cls._validate_formatters_exist(doc)
        cls._validate_personas_consistent(doc)
        cls._validate_no_duplicate_paths(doc)
        cls._validate_field_id_format(doc)
        cls._validate_persona_limits_reasonable(doc)
        return cls(doc)

    @staticmethod
    def _validate_formatters_exist(doc: FieldRegistryDoc) -> None:
        from agent.rendering.formatters import FORMATTERS

        missing = [fid for fid, fd in doc.fields.items() if fd.formatter not in FORMATTERS]
        if missing:
            raise FieldRegistryError(f"Unknown formatter on fields: {missing}")

    @staticmethod
    def _validate_personas_consistent(doc: FieldRegistryDoc) -> None:
        known = set(doc.personas.keys())
        unknown = {
            persona
            for fd in doc.fields.values()
            for persona in fd.default_visibility.keys()
            if persona not in known
        }
        if unknown:
            raise FieldRegistryError(f"Unknown personas in default_visibility: {sorted(unknown)}")

    @staticmethod
    def _validate_no_duplicate_paths(doc: FieldRegistryDoc) -> None:
        seen: dict[str, str] = {}
        for field_id, field in doc.fields.items():
            if field.path in seen:
                LOG.warning("Duplicate registry path: %s (%s, %s)", field.path, seen[field.path], field_id)
            seen[field.path] = field_id

    @staticmethod
    def _validate_field_id_format(doc: FieldRegistryDoc) -> None:
        for field_id in doc.fields:
            if not re.match(_FIELD_ID_RE, field_id):
                raise FieldRegistryError(f"Invalid field id format: {field_id}")

    @staticmethod
    def _validate_persona_limits_reasonable(doc: FieldRegistryDoc) -> None:
        for persona, limits in doc.personas.items():
            if limits.max_primary + limits.max_expandable > 20:
                raise FieldRegistryError(f"Persona limits too large for {persona}")

    def get(self, field_id: str) -> FieldDefinition | None:
        return self._fields.get(field_id)

    def fetch_value(self, field_id: str, context: dict[str, Any]) -> Any:
        field = self.get(field_id)
        if not field:
            return None
        return _resolve_path(context, field.path)

    def format_value(self, field_id: str, value: Any) -> str:
        from agent.rendering.formatters import FORMATTERS

        if value is None:
            return "N/A"
        field = self.get(field_id)
        if not field:
            return str(value)
        fn = FORMATTERS.get(field.formatter)
        return fn(value) if fn else str(value)

    def ids_for_persona(self, persona: str, default_visibility: str | None = None) -> list[str]:
        out: list[str] = []
        for field_id, field in self._fields.items():
            visibility = field.default_visibility.get(persona, "hidden")
            if visibility == "hidden":
                continue
            if default_visibility and visibility != default_visibility:
                continue
            out.append(field_id)
        return out

    def ids_by_decision_weight(self, weight: str, persona: str) -> list[str]:
        visible = set(self.ids_for_persona(persona))
        return [fid for fid, fd in self._fields.items() if fid in visible and fd.decision_weight == weight]

    def as_llm_menu(self, persona: str) -> list[dict]:
        menu = []
        for fid in self.ids_for_persona(persona):
            fd = self._fields[fid]
            menu.append(
                {
                    "field_id": fid,
                    "label": fd.label,
                    "type": fd.type,
                    "decision_weight": fd.decision_weight,
                    "default_visibility": fd.default_visibility.get(persona, "hidden"),
                    "description": fd.description,
                }
            )
        return menu


def _resolve_path(obj: Any, path: str) -> Any:
    current = obj
    for part in path.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            idx = int(part)
            current = current[idx] if 0 <= idx < len(current) else None
        else:
            return None
    return current
