from time import sleep
import asyncio

async def test1():
    print("Test 1 start")
    await asyncio.sleep(1)
    print("Test 1 end")

async def test2():
    print("Test 2 start")
    await asyncio.sleep(2)
    print("Test 2 end")

async def main():
    await test1()
    await test2()

if __name__ == "__main__":
    asyncio.run(main())