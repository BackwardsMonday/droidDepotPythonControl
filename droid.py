import asyncio
from time import sleep
from bleak import BleakScanner, BleakClient
class droid():
    def __init__(self, ipAdress):
        print("initizing")
        self.ipAdress = ipAdress
        self.connection = asyncio.run(self.connect())
    async def connect(self):
        print("connecting")
        async with BleakClient(self.ipAdress) as droid:
            await droid.write_gatt_char(0x000d, 222001)
            await droid.write_gatt_char(0x000d, 222001)


arms = droid("D4:D7:12:C5:93:C1")