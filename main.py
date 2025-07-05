from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import JSONResponse
import httpx
import re

app = FastAPI()

@app.get("/gameinfo")
async def gameinfo(q: str = Query(..., description="Roblox game URL")):
    try:
        # Extract placeId
        match = re.search(r"/games/(\d+)", q)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid Roblox link (placeId not found)")
        place_id = match.group(1)

        # Fetch universeId
        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
            uni_res = await client.get(f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
            if uni_res.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to get universeId")
            universe_id = uni_res.json().get("universeId")
            if not universe_id:
                raise HTTPException(status_code=500, detail="universeId missing from response")

            # Fetch game info
            game_res = await client.get(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
            if game_res.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to get game info")
            data = game_res.json().get("data", [])
            if not data:
                raise HTTPException(status_code=404, detail="No game info found")

        return JSONResponse(content={"result": "success", "response": data[0]})

    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": "error", "error": str(e)})
