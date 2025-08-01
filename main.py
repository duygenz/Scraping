import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Powerful Scraping API",
    description="An API using FastAPI and Playwright to scrape dynamic web pages.",
    version="1.0.0",
)

# Pydantic model để xác thực dữ liệu đầu vào
class ScrapeRequest(BaseModel):
    url: str = Field(..., example="https://quotes.toscrape.com/js/")
    # Thêm các tùy chọn khác nếu muốn, ví dụ:
    # selector: str | None = None # Lấy element cụ thể
    # wait_for_network: bool = True # Chờ cho mạng ổn định

# Endpoint chính của API
@app.post("/scrape")
async def scrape_website(request: ScrapeRequest):
    """
    Nhận một URL, truy cập bằng trình duyệt headless (không giao diện),
    chờ cho nội dung động tải xong, và trả về toàn bộ HTML của trang.
    """
    async with async_playwright() as p:
        try:
            # Khởi chạy trình duyệt Chromium
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Truy cập URL
            await page.goto(request.url, wait_until="networkidle", timeout=15000)

            # Lấy nội dung HTML của trang sau khi JavaScript đã chạy
            content = await page.content()

            # Đóng trình duyệt
            await browser.close()

            # (Tùy chọn) Dùng BeautifulSoup để trích xuất dữ liệu cụ thể
            # Ví dụ: lấy tất cả các câu quote
            soup = BeautifulSoup(content, 'html.parser')
            quotes = [q.get_text(strip=True) for q in soup.select('.quote .text')]

            return {
                "url": request.url,
                "scraped_quotes": quotes,
                "full_html_length": len(content)
            }

        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail=f"Timeout error when trying to access {request.url}. The page might be too slow or unreachable.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Endpoint gốc để kiểm tra API có hoạt động không
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Powerful Scraping API!"}
