from datetime import datetime
from pydantic import BaseModel

class UserActivity(BaseModel):
      id: int
      user_id: int
      action: str
      timestamp: datetime
      detail: str