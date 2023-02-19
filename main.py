import os.path
from typing import List

import uvicorn
from fastapi import FastAPI, File, UploadFile, Body

from BaseModels.ImageModel import VehicleCountResponse
from BaseStation.code.basestation_main import BasestationMain
from Cloud.cloud_main import CloudMain

send_all_together = True

dir_path = "BaseStation/code/Basestation_Images"

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

if not os.path.exists(dir_path):
    os.mkdir(dir_path)
    print("Directory created.")
else:
    print("Directory already exists.")


# @app.get("/hello")
# async def hello():
#     return "Hello"


@app.post("/cloud/information")
async def cloud1(road_info: dict = Body(...)):
    print("road_info")
    service = CloudMain()
    response = service.road_check(road_info)

    return response


@app.post("/import/images/{num_pic}", response_model=VehicleCountResponse)
async def drone(num_pic: int, files: List[UploadFile] = File(...)):
    service = BasestationMain()
    if send_all_together:
        response = service.all_together(files)
    else:
        response = service.divide_in_segments(files, num_pic)
    print("cloud...")

    return VehicleCountResponse(
        cars_per_pic=response
    )
