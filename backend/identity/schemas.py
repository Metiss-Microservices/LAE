from pydantic import BaseModel


class SupplierRegisterSchema(BaseModel):

    phone: str

    password: str

    full_name: str

    category_id: str

    subcategory_id: str

    location_id: str


class SupplierLoginSchema(BaseModel):

    phone: str

    password: str


class ClientLoginSchema(BaseModel):

    phone: str

    code: str


class SessionResponse(BaseModel):

    success: bool

    token: str | None = None
