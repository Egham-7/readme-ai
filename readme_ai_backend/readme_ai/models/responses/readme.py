from typing_extensions import List
from pydantic import BaseModel
from readme_ai.models.requests.readme import Readme


class ReadmesResponse(BaseModel):
    data: List[Readme]
    total_pages: int
