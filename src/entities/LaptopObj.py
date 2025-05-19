from pydantic import BaseModel

class Laptop(BaseModel):
      id: int
      user_id: int
      brand: str
      cpu: str
      gpu: str
      min_price: int
      max_price: int