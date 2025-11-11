import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.tools.chroma_client import ingest, query
from app.tools.chunking import simple_chunk

text = """CT 肺结节分割是医学影像中的重要任务。
它用于辅助医生在 CT 图像中检测和提取结节区域。
目前主流方法包括 3D U-Net、SwinUNETR 等。"""

chunks = simple_chunk(text, source="demo")
ingest(chunks)
res = query("CT 结节分割方法")
print(res)
