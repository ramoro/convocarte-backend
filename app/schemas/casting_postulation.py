from pydantic import BaseModel

class Role(BaseModel):
    id: int
    name: str

class ExposedRole(BaseModel):
    id: int
    role: Role

class CastingCall(BaseModel):
    id: int
    title: str
    state: str
    remuneration_type: str

class CastingPostulationResponse(BaseModel):
    id: int
    state: str
    postulation_data: str
    casting_call: CastingCall
    exposed_role: ExposedRole