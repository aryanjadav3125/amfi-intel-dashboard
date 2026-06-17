from datetime import date
from typing import Optional
from pydantic import BaseModel

class NavHistoryPoint(BaseModel):
    date: date
    nav: float
    regular_nav: Optional[float] = None
