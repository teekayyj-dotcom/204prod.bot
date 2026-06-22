import json
import logging
import google.generativeai as genai
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# System prompt to guide Gemini to return specific JSON structure
PROMPT = """
Bạn là một trợ lý ảo phân tích chi phí cho một đoàn làm phim.
Dựa vào đoạn văn bản hoặc hình ảnh người dùng cung cấp, hãy trích xuất 2 thông tin chính và trả về DUY NHẤT một chuỗi JSON hợp lệ với định dạng sau, KHÔNG có markdown, KHÔNG giải thích thêm:
{
  "hang_muc": "<Một trong các hạng mục sau: 'Ăn uống', 'Di chuyển', 'Thiết bị', 'Lưu trú', 'Khác'>",
  "so_tien": <Số tiền dưới dạng số nguyên, ví dụ: 450000>
}
Nếu không thể xác định được số tiền hoặc hạng mục, hãy cố gắng suy luận hợp lý hoặc dùng hạng mục 'Khác'. Nếu hoàn toàn không thể nhận diện, trả về JSON rỗng {}.
"""

async def parse_expense_text(text: str) -> Optional[Dict]:
    """Parse expense from free-text using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([PROMPT, text])
        result_text = response.text.strip()
        
        # Strip potential markdown formatting from Gemini response
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text.strip())
        return data if "hang_muc" in data and "so_tien" in data else None
    except Exception as e:
        logger.error(f"Error parsing text with Gemini: {e}")
        return None

async def parse_expense_image(image_bytes: bytes, mime_type: str) -> Optional[Dict]:
    """Parse expense from an image using Gemini multimodal."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prepare the image part
        image_part = {
            "mime_type": mime_type,
            "data": image_bytes
        }
        
        response = model.generate_content([PROMPT, image_part])
        result_text = response.text.strip()
        
        # Strip potential markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text.strip())
        return data if "hang_muc" in data and "so_tien" in data else None
    except Exception as e:
        logger.error(f"Error parsing image with Gemini: {e}")
        return None
