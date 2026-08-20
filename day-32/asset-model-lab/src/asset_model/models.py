from dataclasses import dataclass


@dataclass
class Asset:
    asset_id: str
    hostname: str
    port: int
    active: bool
    tags: list[str]
