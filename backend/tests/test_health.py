async def test_live_health(client) -> None:
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["version"] == "0.3.0"
