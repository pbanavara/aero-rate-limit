"""
A sample web application to demonstrate the Aerospike quota system.
The user quotauser here is configured on Aerospike with rate limits.
We expect the program to behave according the rate limits and raise appropriate exceptions.

Author: Pradeep Banavara
"""
import aerospike
from aerospike import exception
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

AEROSPIKE_HOST = "0.0.0.0"
NAMESPACE = "test"
SET = "testset"
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: int

class TPS(BaseModel):
    read_tps: int
    write_tps: int

app = FastAPI()
config = {
  'hosts': [ (AEROSPIKE_HOST, 3000) ]
}
client = aerospike.client(config)
"""
Placeholder just to set the quotas. To be refactored into a separate app
client = aerospike.client(config).connect('admin', 'admin')
"""

@app.post("/admin/tps")
def set_tps(tps: TPS):
    client.connect('admin', 'admin')
    client.admin_set_quotas(role='worker', read_quota=tps.read_tps, write_quota=tps.write_tps)
    role_writer = client.admin_get_role('worker')
    client.close()
    return {"Written TPS": role_writer}

@app.post("/connect")
def connect():
    """To reconnect after setting the quota from the above admin/tps URL

    Raises:
        HTTPException: [description]

    Returns:
        [type]: [description]
    """
    try:
        client.connect('quotauser', 'pass')
        return {"message": "Connection established successfully"}
    except exception as e:
        raise HTTPException(status_code=500, detail="Connection refused")


@app.post("/data")
def write_data(item: Item):
    """ A simple function to test quotas by writing data. To test we fire apache bench on this POST request at a high concurrency level.

    Args:
        item (Item): Self explanatory

    Raises:
        HTTPException: [description]

    Returns:
        [json]: [Just the write success or failure]
    """
    key = (NAMESPACE, SET, item.id)
    bin = { "quotabin" : item}
    try :
        client.put(key, bin)
        return { "message" : "Write successful"}
    except exception.QuotaExceeded as qe:
        print("Quota exceeded")
        print(qe)
        raise HTTPException(status_code=429, detail="Too many requests")

@app.get("/data")
def get_data(item: Item):
    try:
        key = (NAMESPACE, SET, item.id)
        _, _, record = client.get(key)
        return record
    except exception.QuotaExceeded as qe:
        raise HTTPException("Quota Exceeeded")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)


