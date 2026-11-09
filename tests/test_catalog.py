"""
Testes unitários para a versão com dados em variável global.
São ruins pois os testes dependem de estado compartilhado
e a ordem altera o resultado esperado.
"""
from fastapi.testclient import TestClient

from app.main import AnimeIn, app

client = TestClient(app)

def test_find_all_with_limit_valid():
    resp = client.get("/animes", params={"limit": 4}).json()
    expected_size: int = 4
    assert len(resp) == expected_size

def test_find_all_with_genre():
    resp = client.get("/animes", params={"genre": "drama"}).json()
    expected_size: int = 2
    assert len(resp) == expected_size

def test_find_all_with_genre_and_limit():
    resp = client.get("/animes", params={"genre": "acao", "limit": 1}).json()
    expected_size: int = 1
    assert len(resp) == expected_size

def test_find_by_slug_should_return_animeout():
    resp = client.get("/animes/jardim-do-silencio")
    assert resp.status_code == 200

def test_find_by_slug_should_return_404_for_invalid_slug():
    invalid_slug: str = "nonslug"
    resp = client.get(f"/animes/{invalid_slug}")
    assert resp.status_code == 404
    assert resp.json()['detail'] == f"Anime {invalid_slug} not found"

def test_post_return_new_anime_with_id():
    anime_in = {
        "title": "Dragon Ball",
        "slug": "dragonball",
        "year": 1986,
        "genres": ["acao", "aventura"]
    }
    resp = client.post("/animes",json=anime_in)
    assert resp.status_code == 201
    assert resp.json()['id'] is not None

def test_post_raises_when_duplicated_slug():
    """Teste ruim pois depende da execução do teste anterior. Será modificado com mocks posteriormente"""
    anime_in = {
        "title": "Dragon Ball",
        "slug": "dragonball",
        "year": 1986,
        "genres": ["acao", "aventura"]
    }
    resp = client.post("/animes",json=anime_in)
    assert resp.status_code == 409

def test_post_returns_location_with_slug():
    anime_in = {
        "title": "Dragon Ball Z",
        "slug": "dragonballz",
        "year": 1989,
        "genres": ["acao", "aventura"],
    }
    slug_url: str = f"http://localhost:8080/animes/{anime_in['slug']}"
    resp = client.post("/animes", json=anime_in)
    assert resp.headers.get('Location') == slug_url

def test_post_with_invalid_slug_returns_422():
    invalid_slug: str = "%No T a V@al1D slg"
    anime_in = {
        "title": "Dragon Ball Z",
        "slug": invalid_slug,
        "year": 1989,
        "genres": ["acao", "aventura"],
    }
    resp = client.post("/animes", json=anime_in)
    assert resp.status_code == 422
    assert resp.json()['detail'] is not None

def test_delete_returns_204():
    slug: str = "any-slug"
    resp = client.delete(f"/animes/{slug}")
    assert resp.status_code == 204