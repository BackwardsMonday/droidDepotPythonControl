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
        light_blink = bytearray.fromhex("2C000449020001ff01ff0aff00")
        await self.droid.write_gatt_char(0x000d, light_blink)
        connect_sound = bytearray.fromhex("25000c421102")
        await self.droid.write_gatt_char(0x000d, connect_sound)
        sleep(3)

    async def disconnect(self):
        print ("Disconnecting")
        try:
            soundBank = bytearray.fromhex("27420f4444001f09")
            await self.droid.write_gatt_char(0x000d, soundBank)
            soundSelection = bytearray.fromhex("27420f4444001800")
            await self.droid.write_gatt_char(0x000d, soundSelection)
            sleep(3)
        finally:
            await self.droid.disconnect()
            print("Disconnected")

    async def play_sound(self, sound_id=None, bank_id=None, cycle=False):
        if bank_id and self.soundbank != bank_id:
            self.set_soundbank(bank_id)
        if sound_id:
            soundSelection = bytearray.fromhex("27420f44440018{}".format(sound_id))
        elif cycle:
            soundSelection = bytearray.fromhex("26420f4344001c")
        else:
            soundSelection = bytearray.fromhex("27420f44440010{}".format(self.bank_id))
        await self.droid.write_gatt_char(0x000d, soundSelection)

    async def run_routine(self, routineId):
        full_id = bytearray.fromhex("25000c42{}02".format(routineId))
        await self.droid.write_gatt_char(0x000d, full_id)
    
    async def set_soundbank(self, bank_id):
        self.soundbank = bank_id
        soundBank = bytearray.fromhex("27420f4444001f{}".format(bank_id))
        await self.droid.write_gatt_char(0x000d, soundBank)

    async def set_volume(self, volume):
        volume_command = bytearray.fromhex("27420f4444000e{}".format(volume))
        await self.droid.write_gatt_char(0x000d, volume_command)
    
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
        sleep (5)
        await arms.set_soundbank("05")
        await arms.play_sound("00")
        sleep (5)
        for i in range(5):
            await arms.play_sound(cycle=True)
            sleep(5)
        await arms.play_sound("00", "00")

    finally:
        await arms.disconnect()
asyncio.run(main())