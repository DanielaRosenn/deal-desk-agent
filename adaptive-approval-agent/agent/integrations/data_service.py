class DataServiceClient:
    def __init__(self, settings):
        self.settings = settings
        self._store: dict[str, dict] = {}

    def write(self, entity: str, key: str, data: dict) -> None:
        self._store[f"{entity}:{key}"] = dict(data)

    def read(self, entity: str, key: str) -> dict | None:
        return self._store.get(f"{entity}:{key}")
