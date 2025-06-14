# filename: app.py

from fastapi import FastAPI, Body
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os

from fastapi.responses import FileResponse

app = FastAPI()


# Định nghĩa dữ liệu đầu vào
class InputData(BaseModel):
    avatar_url: str
    message: str
    name: str
    faculty: str


# Tạo thư mục lưu ảnh output nếu chưa có
OUTPUT_DIR = "output_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load sẵn template
TEMPLATE_PATH = "template.png"  # Đổi tên file template bạn tải về
FONT_PATH = "arial.ttf"  # Bạn cần chuẩn bị file font, ví dụ Arial


@app.post("/process-image/")
async def process_image(data: InputData):
    # Tải template
    template = Image.open(TEMPLATE_PATH).convert("RGBA")

    # Tải avatar
    response = requests.get(data.avatar_url)
    avatar = Image.open(io.BytesIO(response.content)).convert("RGBA")

    # Resize avatar vuông rồi paste lên vị trí phù hợp (điều chỉnh tuỳ file)
    avatar = avatar.resize((200, 200))
    template.paste(avatar, (80, 180), mask=avatar)  # Toạ độ hình tròn bên trái

    # Thêm thông điệp & tên khoa
    draw = ImageDraw.Draw(template)
    font_message = ImageFont.truetype(FONT_PATH, size=36)
    font_name = ImageFont.truetype(FONT_PATH, size=28)

    # Vị trí box thông điệp: chỉnh tuỳ template bạn
    draw.text((420, 250), data.message, font=font_message, fill="blue")

    # Vị trí text tên & khoa
    draw.text((90, 420), f"{data.name} - Khoa {data.faculty}", font=font_name, fill="white")

    # Lưu file output
    filename = f"{data.name.replace(' ', '_')}_output.png"
    output_path = os.path.join(OUTPUT_DIR, filename)
    template.save(output_path)

    # Trả file đã ghép
    return FileResponse(output_path, media_type="image/png")
