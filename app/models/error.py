from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    code: str = Field(..., description="错误码，例如 E_API_TIMEOUT")
    message: str = Field(..., description="用户可读的错误信息")
    hint: str | None = Field(None, description="可选，告诉前端下一步怎么做")