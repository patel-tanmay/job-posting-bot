from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import JobPosting, QuerySpec


class JobSourceAdapter(ABC):
    source_name: str

    @abstractmethod
    def search(self, query: QuerySpec, max_results: int, max_pages: int = 1) -> List[JobPosting]:
        raise NotImplementedError
