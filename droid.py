import asyncio
from time import sleep
from bleak import BleakScanner, BleakClient
import pickle
class Droid():
    def __init__(self, profile):
        print("Initializing")
        self.disabledLeds = 0x00
        self.profile = profile

    # assumes theta in degrees and r = 0 to 100 %
    # returns a tuple of percentages: (left_thrust, right_thrust)
    def __throttle_angle_to_thrust__(r, theta):
        theta = ((theta + 180) % 360) - 180  # normalize value to [-180, 180)
        r = min(max(0, r), 100)              # normalize value to [0, 100]
        v_a = r * (45 - theta % 90) / 45          # falloff of main motor
        v_b = min(100, 2 * r + v_a, 2 * r - v_a)  # compensation of other motor
        if theta < -90: return -v_b, -v_a
        if theta < 0:   return -v_a, v_b
        if theta < 90:  return v_b, v_a
        return v_a, -v_b
    
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
    
    async def led_disable_sound(self, leds):
        ledDisableCommand = bytearray.fromhex(f"27420f4444004a{leds}")
        await self.droid.write_gatt_char(0x000d, ledDisableCommand)
        self.disabledLeds = self.disabledLeds|int(leds, 16)
        print(self.disabledLeds)

    async def led_enable_sound(self, leds):
        ledEnableCommand = bytearray.fromhex(f"27420f4444004b{leds}")
        await self.droid.write_gatt_char(0x000d, ledEnableCommand)
        self.disabledLeds = self.disabledLeds-(int(leds, 16)&self.disabledLeds)
        print(self.disabledLeds)
        
    
    async def led_flash(self, leds, duration):
        pass
    
    async def led_off(self, leds):
        ledOffCommand = bytearray.fromhex( f"27420f44440049{leds}" )
        await self.droid.write_gatt_char(0x000d, ledOffCommand)
        print(f"{self.disabledLeds:02x}")
        print((f"{(~self.disabledLeds & 0x1F):02x}"))
        await self.led_enable_sound(f"{(~self.disabledLeds & 0x1F):02x}")

    
    async def led_on(self, leds):
        ledOnCommand = bytearray.fromhex(f"27420f44440048{leds}")
        await self.droid.write_gatt_char(0x000d, ledOnCommand)
    
    def move (self, degrees, duration):
        thrust = self.__throttle_angle_to_thrust__(degrees)
        
    async def play_sound(self, sound_id=None, bank_id=None, cycle=False, volume=None):
        if volume:
            self.set_volume(volume)
        if bank_id and (not hasattr(self, "soundbank") or self.soundbank != bank_id):
            await self.set_soundbank(bank_id)
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
        # await arms.run_routine("05")
        # sleep (5)
        # await arms.set_soundbank("05")
        # await arms.play_sound("00")
        # sleep (5)
        # for i in range(5):
        #     await arms.play_sound(cycle=True)
        #     sleep(5)
        # await arms.play_sound("00", "00")
        # sleep(8)
        await arms.led_disable_sound("01")
        await arms.play_sound("00", "00")
        sleep(10)
        await arms.led_on("1f")
        sleep(10)
        await arms.led_off("1f")
        await arms.play_sound("00", "00")
        sleep(10)


    finally:
        await arms.disconnect()
asyncio.run(main())