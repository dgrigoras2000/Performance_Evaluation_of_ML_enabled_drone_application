from pydantic import BaseModel


class VehicleCountResponse(BaseModel):
    cars_per_pic: dict


class CarsPerPictureRequest(BaseModel):
    cars_per_pic: dict


class CarsPerPictureResponse(BaseModel):
    received: bool
