from typing import Union
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.utils.vidguard import get_video_url

CORS = {
    "origins": ["*"],
    # "allow_methods": ["*"],
    # "allow_headers": ["*"],
}

app = FastAPI()
# app.add_middleware(CORSMiddleware, **CORS)


class Item(BaseModel):
    url: str


@app.get("/")
def read_root():
    return {
        "Hello": "Welcome to the vidguard.to data extraction API to block annoying and obscene ads. It is very easy to use, just embed your embed and extract a link that works for 5 minutes of download."
    }


@app.post("/extract")
async def extract_endpoint(item: Item):
    try:
        url = get_video_url(item.url)
        return {"url": f"http://45.88.9.31:8001/proxy?url={url}"}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
