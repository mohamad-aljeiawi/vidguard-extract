import uvicorn
from fastapi import FastAPI, Request as FastAPIRequest, HTTPException
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from urllib.parse import urljoin, urlencode, quote_plus, urlparse, urlunparse
from src.utils.vidguard import get_video_url
from src.utils.utils import is_valid_url
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
PORT = os.getenv("PORT")

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

        # Make sure we properly encode the URL to preserve all query parameters
        encoded_url = quote_plus(url)

        # return ResponseExtract(url=f"http://45.88.9.31:8002/proxy_stream?url={encoded_url}")
        return ResponseExtract(url=f"{BASE_URL}/proxy_stream?url={encoded_url}")

    except Exception as e:
        return {"error": str(e)}


@app.get("/proxy_stream")
async def proxy_stream(url: str):  # FastAPI يفك التشفير تلقائيا من query param
    if not url or not is_valid_url(url):
        raise HTTPException(
            status_code=400, detail="Missing or invalid 'url' parameter"
        )

    # Remove any @ character at the beginning of the URL if it exists
    if url.startswith("@"):
        url = url[1:]

    print(f"Proxying request for: {url}")

    try:
        # طلب المحتوى من VidGuard باستخدام IP الـ VPS
        # تمرير بعض الهيدرات الشائعة قد يساعد
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://vidguard.to/",  # قد تحتاج لتغيير الريفيرير
        }

        response = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        # رفع الخطأ إذا لم تنجح VidGuard في الرد
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        print(f"VidGuard responded with Content-Type: {content_type}")

        # === معالجة M3U8 ===
        if "mpegurl" in content_type or "x-mpegurl" in content_type:
            # قراءة محتوى M3U8 كنص
            m3u8_content = response.text
            print(f"Processing M3U8 content (first 200 chars):\n{m3u8_content[:200]}")

            # تحليل وإعادة كتابة الروابط
            rewritten_lines = []
            base_url = url  # الرابط الأصلي لـ M3U8 هذا

            for line in m3u8_content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    # الاحتفاظ بالتعليقات والأسطر الفارغة كما هي
                    rewritten_lines.append(line)
                    continue

                # هذا السطر هو رابط (إما ملف M3U8 آخر أو مقطع TS)
                original_segment_url = line
                # بناء الرابط المطلق إذا كان نسبيًا
                absolute_segment_url = urljoin(base_url, original_segment_url)

                # تشفير رابط المقطع الأصلي
                encoded_segment_url = quote_plus(absolute_segment_url)

                # إنشاء رابط البروكسي الجديد لهذا المقطع
                # يستخدم نفس Endpoint (/proxy_stream)
                proxy_segment_url = f"{BASE_URL}/proxy_stream?url={encoded_segment_url}"  # استخدام رابط نسبي للبروكسي

                print(f"  Rewriting: {original_segment_url} -> {proxy_segment_url}")
                rewritten_lines.append(proxy_segment_url)

            # إعادة M3U8 المعدل
            final_m3u8 = "\n".join(rewritten_lines)
            return Response(
                content=final_m3u8, media_type="application/vnd.apple.mpegurl"
            )

        # === معالجة مقاطع الفيديو (TS) أو أي شيء آخر ===
        else:
            print(f"Streaming content directly (Content-Type: {content_type})")
            # بث المحتوى مباشرة للعميل

            def iterfile():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            return StreamingResponse(
                iterfile(),
                media_type=content_type,
                headers={
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() in ["content-length", "content-type"]
                },
            )  # تمرير الهيدرات المهمة

    except requests.RequestException as exc:
        print(f"HTTP Request Error during proxy: {exc}")
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch from origin server: {exc}"
        )
    except Exception as e:
        print(f"Generic error during proxy: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
