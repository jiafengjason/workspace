import os
import shutil
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse, JSONResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
async def show_upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": filename, "message": "文件上传成功"}

@app.get("/redirect")
async def redirect():
    return RedirectResponse(url="https://wd.enlink.top")

@app.post("/post-data")
async def post_data(data: dict):
    # 这里我们简单返回接收到的数据
    return JSONResponse(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
