from abc import ABC, abstractmethod
from typing import Any


class JobSource(ABC):
    """Common interface for every job source (API or scraper)."""

    name: str = "base"

    @abstractmethod
    def fetch(self, query: str = "", **kwargs: Any) -> list[dict]:
        """Return a list of normalized job dicts:

        {
          "source": str,            # e.g. "remotive"
          "external_id": str,
          "title": str,
          "company": str | None,
          "location": str | None,
          "remote": bool,
          "url": str | None,
          "description": str,
          "posted_at": datetime | None,
        }
        """
        raise NotImplementedError
