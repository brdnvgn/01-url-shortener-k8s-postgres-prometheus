"""Business endpoints: short link creation and redirection."""

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import RedirectResponse

from .config import settings
from .metrics import LINKS_CREATED, REDIRECTS
from .repository import create_short_link, resolve_and_count
from .schemas import ShortenRequest, ShortenResponse

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=201)
async def shorten(payload: ShortenRequest, request: Request) -> ShortenResponse:
    """Creates a short code for the given URL and persists it in PostgreSQL."""
    code = await create_short_link(str(payload.url), settings.code_length)
    LINKS_CREATED.inc()
    short_url = f"{str(request.base_url).rstrip('/')}/{code}"
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
