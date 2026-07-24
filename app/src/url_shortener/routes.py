"""Business endpoints: short link creation and redirection."""

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import RedirectResponse

from .config import settings
from .metrics import LINKS_CREATED, REDIRECTS
from .repository import create_short_link, resolve_and_count
from .schemas import ShortenRequest, ShortenResponse

router = APIRouter()


def _public_base_url(request: Request) -> str:
    """Determines the externally visible base URL for the returned short link.

    `request.base_url` reflects the internal ASGI connection, which is wrong
    behind a Kubernetes Ingress or reverse proxy. Prefer an explicitly
    configured `PUBLIC_BASE_URL`, then standard forwarded headers set by the
    proxy, and only fall back to the raw ASGI base URL for local/direct use.
    """
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")

    forwarded_host = request.headers.get("x-forwarded-host")
    if forwarded_host:
        forwarded_proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        return f"{forwarded_proto}://{forwarded_host}"

    return str(request.base_url).rstrip("/")


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten(payload: ShortenRequest, request: Request) -> ShortenResponse:
    """Creates a short code for the given URL and persists it in PostgreSQL."""
    code = await create_short_link(str(payload.url), settings.code_length)
    LINKS_CREATED.inc()
    short_url = f"{_public_base_url(request)}/{code}"
    return ShortenResponse(code=code, short_url=short_url)


@router.get("/{code}")
async def redirect(
    code: str = Path(pattern=r"^[0-9A-Za-z]{1,10}$"),
) -> RedirectResponse:
    """Resolves the code to the original URL and redirects (HTTP 302)."""
    long_url = await resolve_and_count(code)
    if long_url is None:
        raise HTTPException(status_code=404, detail="Code not found.")
    REDIRECTS.inc()
    return RedirectResponse(url=long_url, status_code=302)
