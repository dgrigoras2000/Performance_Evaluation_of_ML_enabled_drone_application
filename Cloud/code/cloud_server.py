import uvicorn
from fastapi import FastAPI, Body

from cloud_main import CloudMain

send_all_together = True

dir_path = "/BaseStation/Basestation_Images"

app2 = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app2, host="127.0.0.1", port=8001)


@app2.post("/cloud/information")
async def cloud1(road_info: dict = Body(...)):
    print("road_info")
    service = CloudMain()
    response = service.road_check(road_info)

    return response
