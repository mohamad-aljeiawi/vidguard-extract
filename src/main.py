import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from src.utils.vidguard import get_video_url
from src.utils.utils import is_valid_url

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "Hello": "Welcome to the vidguard.to data extraction API to block annoying and obscene ads. It is very easy to use, just embed your embed and extract a link that works for 5 minutes of download."
    }


class RequestExtract(BaseModel):
    url: str


class ResponseExtract(BaseModel):
    url: str


@app.post("/extract")
async def extract_endpoint(request: RequestExtract):
    try:
        if not is_valid_url(request.url):
            raise ValueError("Invalid URL")
        url: str = get_video_url(request.url)
        return ResponseExtract(url=f"http://45.88.9.31:8001/proxy?url={url}")

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
