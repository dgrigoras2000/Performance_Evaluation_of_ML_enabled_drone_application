import os.path
import logging
from typing import List

from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from pydantic import BaseModel

from basestation_main import BasestationMain

USE_FOLDER_FOR_SAVE = bool(os.environ['USE_FOLDER_FOR_SAVE'])
SEND_ALL_TOGETHER = bool(os.environ['SEND_ALL_TOGETHER'])

dir_path = "Basestation_Images"

app1 = FastAPI()


class VehicleCountResponse(BaseModel):
    cars_per_pic: dict


@app1.get("/check/connection")
async def check_conn():
    return "Connection established"


@app1.post("/import/images/{num_pic}", response_model=VehicleCountResponse)
async def drone(num_pic: int, files: List[UploadFile] = File(...)):
    service = BasestationMain()
    if SEND_ALL_TOGETHER:
        response = service.all_together(files)
    else:
        response = service.divide_in_segments(files, num_pic)
    print("cloud...")
    # response1 = await service.send_to_cloud(response)
    # print(response1)

    return VehicleCountResponse(
        cars_per_pic=response
    )


if __name__ == "__main__":
    import uvicorn
    import shutil

    if USE_FOLDER_FOR_SAVE:
        if os.path.exists(dir_path):
            print("Directory already exists.")
        else:
            os.mkdir(dir_path)
            print("Directory created.")

    # Check if the server is alive
    try:
        # Start the server in a separate thread
        uvicorn.run(f"basestation_server:app1", host="0.0.0.0", port=8000, reload=True)

    except KeyboardInterrupt:
        shutil.rmtree(dir_path)
        print("Server has stopped")
