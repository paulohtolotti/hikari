import logging
import time
from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hikari API")


class AnimeIn(BaseModel):
    """Registration data"""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "slug": "fullmetal-brotherhood",
                    "title": "Fullmetal Alchemist Brotherhood",
                    "year": 2010,
                    "genres": ["acao", "drama", "misterio"],
                }
            ]
        }
    )
    slug: str = Field(
        pattern=r"^[a-z0-9-]{2,120}$"
    )  # URL unique identifier. Ex: /animes/fullmetal
    title: str = Field(min_length=2, max_length=255)
    year: int = Field(ge=1950, le=2900)
    genres: list[str] = []


class AnimeOut(AnimeIn):
    """Response. Includes everything of the mother class plus an id"""

    id: int


ANIMES: list[AnimeOut] = [
    AnimeOut(
        id=1,
        slug="cacadores-de-nuvens",
        title="Caçadores de Nuvens",
        year=2025,
        genres=["aventura", "fantasia"],
    ),
    AnimeOut(
        id=2,
        slug="chef-de-ferro",
        title="Chef de Ferro",
        year=2026,
        genres=["comedia", "culinaria"],
    ),
    AnimeOut(
        id=3, slug="eco-neon", title="Eco Neon", year=2026, genres=["acao", "ficcao"]
    ),
    AnimeOut(
        id=4,
        slug="jardim-do-silencio",
        title="Jardim do Silêncio",
        year=2024,
        genres=["drama"],
    ),
    AnimeOut(
        id=5,
        slug="arslan-senki",
        title="Arslan Senki",
        year=2016,
        genres=["drama", "acao"],
    ),
]


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "running & up", "message": "hikari hi"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/animes", status_code=status.HTTP_200_OK, response_model=list[AnimeOut])
async def find_all(
    limit: Annotated[
        int, Query(ge=1, lt=50, description="Maximum number of records to be fetched")
    ] = 20,
    genre: Annotated[str | None, Query(description="Genre to be filtered")] = None,
) -> list[AnimeOut]:
    """
    Find all animes paginated
    """
    logger.info("Query params: limit %s, genre %s", limit, genre)

    response = (
        list(filter(lambda a: genre.lower() in a.genres, ANIMES)) if genre else ANIMES
    )
    response.sort(key=lambda k: k.title)
    logger.info("Response created for find_all: %s", response)
    return response[:limit]


@app.get("/animes/{slug}", status_code=status.HTTP_200_OK, response_model=AnimeOut)
async def find_by_slug(slug: str):
    logger.info("Finding by slug %s", slug)
    response = [x for x in ANIMES if x.slug.lower() == slug.lower()]
    if not response:
        logger.info("Slug not found %s. Raising", slug)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Anime {slug} not found"
        )
    logger.info("Slug found %s", response[0])
    return response[0]


@app.post("/animes", status_code=status.HTTP_201_CREATED, response_model=AnimeOut)
async def create(anime_req: AnimeIn, response: Response):
    if anime_req.slug in [a.slug for a in ANIMES]:
        logger.error("%s already registered", anime_req.slug)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{anime_req.slug} already registered",
        )

    anime_resp = AnimeOut(id=len(ANIMES) + 1, **anime_req.model_dump())
    ANIMES.append(anime_resp)
    response.headers["Location"] = f"http://localhost:8080/animes/{anime_resp.slug}"
    return anime_resp


@app.delete(
    "/animes/{slug}", status_code=status.HTTP_204_NO_CONTENT, response_model=None
)
async def delete(slug: str):
    for anime in ANIMES:
        if anime.slug == slug:
            ANIMES.remove(anime)


@app.get("/lenta/bloqueante")
async def slow_blocking():
    """Simula uma operação bloqueante em uma rota async.
    Trava as outras requisições por 10 segundos
    """
    time.sleep(10)  # noqa: ASYNC251
    return {"status": "Dormi 5 segundos"}


@app.get("/lenta/naobloqueante")
def slow_non_blocking():
    """Simula uma operação bloqueante em uma rota def.
    Trava as outras requisições por 10 segundos
    """
    time.sleep(10)
    return {"status": "Dormi 5 segundos"}


if __name__ == "__main__":
    print(ANIMES)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
