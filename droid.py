import asyncio
from time import sleep
from bleak import BleakScanner, BleakClient
class Droid():
    def __init__(self, profile):
        print("Initializing")
        self.profile = profile
    async def connect(self):
        timeout=0.0
        print("Connecting")
        self.droid = BleakClient(self.profile)
        await self.droid.connect()
        while not self.droid.is_connected and timeout < 10:
            sleep (.1)
            timeout += .1
        print ("Connected!")
        connectCode = bytearray.fromhex("222001")
        await self.droid.write_gatt_char(0x000d, connectCode, False)
        await self.droid.write_gatt_char(0x000d, connectCode, False)
        print("Locked")
        soundBank = bytearray.fromhex("27420f4444001f00")
        await self.droid.write_gatt_char(0x000d, soundBank)
        soundSelection = bytearray.fromhex("27420f4444001800")
        await self.droid.write_gatt_char(0x000d, soundSelection)

    async def disconnect(self):
        print ("Disconnecting")
        try:
            soundBank = bytearray.fromhex("27420f4444001f08")
            await self.droid.write_gatt_char(0x000d, soundBank)
            soundSelection = bytearray.fromhex("27420f4444001808")
            await self.droid.write_gatt_char(0x000d, soundSelection)
        finally:
            await self.droid.disconnect()
            print("Disconnected")

    async def run_routine(self, routineId):
        full_id = bytearray.fromhex("25000c42{}02".format(routineId))
        await self.droid.write_gatt_char(0x000d, full_id)
        
def findDroid(candidate, data):
    if candidate.name == "DROID":
        return True
    else:
        return False

async def main():
    myDroid = await BleakScanner.find_device_by_filter(findDroid)
    print (myDroid)
    arms = Droid(myDroid)
    await arms.connect()
    sleep (3)
    try:
        await arms.run_routine("05")
        sleep (3)
    finally:
        await arms.disconnect()
asyncio.run(main())