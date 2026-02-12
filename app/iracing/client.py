import httpx


async def iracing_get(url: str, token: str):
    async with httpx.AsyncClient() as client:
        # Step 1: call the iRacing API endpoint
        print(token, url)
        resp = await client.get(
            url,
            headers={"Authorization": f"Bearer {token}"}
        )

    if resp.status_code != 200:
        raise Exception(f"iRacing API error: {resp.text}")

    data = resp.json()

    # Some endpoints return data directly,
    # but MOST return a "link"
    if "link" not in data:
        # direct payload → return as-is
        return data

    signed_url = data["link"]

    # Step 2: fetch the real JSON from the S3 signed URL
    async with httpx.AsyncClient() as client:
        real_resp = await client.get(signed_url)

    if real_resp.status_code != 200:
        raise Exception(f"Failed to fetch signed data: {real_resp.text}")

    return real_resp.json()
