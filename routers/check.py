import time
from typing import List,Optional
from datetime import datetime
from fastapi import APIRouter, status, Response
from pydantic import BaseModel
from pymongo import MongoClient

db_client = MongoClient("mongodb://localhost:27017/")
db = db_client['scan']
check_collection = db["check"]
status_collection = db["status"]
router = APIRouter(
    tags=["Checkscan"]
)


class Record(BaseModel):
    phone: str
    room: str


@router.post("/check",)
async def check(data: Record, response: Response):
    f = check_collection.find_one({
        "phone": data.phone,
        "room": data.room,
        "check_in_time": {"$exists":True},
        "check_out_time": {"$exists": False}
    })
    if f:
        # want to check out
        check_collection.update_one(f, {
                "$set": {"check_out_time": datetime.now()}
        })
        old = status_collection.find_one({"room": data.room})
        new_data = {"$set": {"count": old["count"]-1}}
        status_collection.update_one(old, new_data)
        response.status_code = status.HTTP_202_ACCEPTED
        return
    else:
        # want to check in
        res = check_collection.insert_one({
            "phone": data.phone,
            "room": data.room,
            "check_in_time": datetime.now()
        })
        old = status_collection.find_one({"room": data.room})
        new_data = {"$set": {"count": old["count"] + 1}}
        status_collection.update_one(old, new_data)
        response.status_code = status.HTTP_200_OK
        return


