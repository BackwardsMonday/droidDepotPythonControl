import asyncio
from time import sleep
from bleak import BleakScanner, BleakClient
class droid():
    def __init__(self, address):
        print("initialing")
        self.address = address
    async def connect(self):
        timeout=0.0
        print("Connecting")
        async with BleakClient(self.address) as droid:
            while not droid.is_connected and timeout < 10:
                sleep (.1)
                timeout += .1
            print ("Connected!")
            connectCode = bytearray.fromhex("222001")
            await droid.write_gatt_char(0x000d, connectCode, False)
            await droid.write_gatt_char(0x000d, connectCode, False)
            print("Locked")
            soundBank = bytearray.fromhex("27420f4444001f00")
            await droid.write_gatt_char(0x000d, soundBank)
            soundSelection = bytearray.fromhex("27420f4444001800")
            await droid.write_gatt_char(0x000d, soundSelection)
def findDroid(candidate, data):
    if candidate.name == "DROID":
        return True
    else:
        return False

async def main():
    myDroid = await BleakScanner.find_device_by_filter(findDroid)
    print (myDroid)
    arms = droid(myDroid)
    await arms.connect()
asyncio.run(main())