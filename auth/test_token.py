import asyncio
from github_app import get_installation_token

async def main():
    installation_id = 74443799  # Replace with your installation ID
    token = await get_installation_token(installation_id)
    print(f"✅ GitHub Token: {token[:10]}...")

asyncio.run(main())
