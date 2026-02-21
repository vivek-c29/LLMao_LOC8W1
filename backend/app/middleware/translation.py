import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.services.gemini_service import translate_text

TRANSLATABLE_FIELDS = {"description", "title", "ai_summary"}
SUPPORTED_LANGUAGES = {"hi", "mr", "te"}


class TranslationMiddleware(BaseHTTPMiddleware):
    """
    Reads X-User-Language header. If a supported non-English language is requested,
    translates 'description' and 'title' fields in JSON GET responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        lang = request.headers.get("X-User-Language", "en").lower()
        if lang not in SUPPORTED_LANGUAGES:
            return response

        # Only translate JSON GET responses
        if request.method != "GET":
            return response
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        # Read and decode body
        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk

        try:
            data = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            return Response(content=body_bytes, status_code=response.status_code,
                            headers=dict(response.headers), media_type=response.media_type)

        # Translate fields recursively
        data = await self._translate_recursive(data, lang)

        new_body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return Response(
            content=new_body,
            status_code=response.status_code,
            headers={**dict(response.headers), "content-length": str(len(new_body))},
            media_type=response.media_type,
        )

    async def _translate_recursive(self, obj, lang: str):
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                if key in TRANSLATABLE_FIELDS and isinstance(obj[key], str):
                    obj[key] = await translate_text(obj[key], lang)
                else:
                    obj[key] = await self._translate_recursive(obj[key], lang)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = await self._translate_recursive(item, lang)
        return obj
