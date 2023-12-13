import asyncio
import scrap


if __name__ == "__main__":
    res = asyncio.run(scrap.run_single_browser_scrap_all("20193018"))
    print(res)
