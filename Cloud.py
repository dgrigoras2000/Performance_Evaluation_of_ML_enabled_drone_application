import uvicorn as uvicorn
from fastapi import FastAPI

from BaseModels.ImageModel import CarsPerPictureRequest
from BaseModels.ImageModel import CarsPerPictureResponse

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8086)


@app.post("/cars/per/picture", response_model=CarsPerPictureResponse)
async def import_image(number_of_cars: CarsPerPictureRequest):
    print(number_of_cars.cars_per_pic)

    return CarsPerPictureResponse(
        received=True
    )
