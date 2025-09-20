# python ble_control.py off 30:AE:A4:1E:26:AE

import asyncio, sys, time
from bleak import BleakScanner, BleakClient

TARGET_NAME = "ESP32-LED"
CHAR_UUID   = "b7e6f2b1-3c7f-4b9d-9c78-1b2a5d5d1e01"

async def discover_match(addr_hint: str | None, burst: float = 4.0) -> "object|None":
    devices = await BleakScanner.discover(timeout=burst)
    # Debug (comment out if noisy)
    # for d in devices:
    #     print(f"{d.address:17}  {str(d.rssi or ''):>4}  {d.name or ''}")
    best = None
    for d in devices:
        by_addr = addr_hint and d.address.lower() == addr_hint.lower()
        by_name = (d.name or "") == TARGET_NAME
        if by_addr or by_name:
            if best is None or (d.rssi or -999) > (best.rssi or -999):
                best = d
    return best

async def connect_and_write(dev_or_addr, payload: bytes, connect_timeout=10.0):
    # Bleak accepts either an address string or a BLEDevice object
    for attempt in range(1, 4):
        try:
            async with BleakClient(dev_or_addr, timeout=connect_timeout) as client:
                await client.write_gatt_char(CHAR_UUID, payload, response=True)
                print("Write OK")
                return True
        except Exception as e:
            print(f"Connect/write attempt {attempt}/3 failed: {e}")
            await asyncio.sleep(0.8 * attempt)
    return False

async def main(state: str, addr_hint: str | None, total_timeout: float = 20.0):
    # NEW (ASCII)
    payload = b"1" if state.lower() in ("on","1","true") else b"0"


    # Fast path: try direct address connect once (works if address is public/static)
    if addr_hint:
        ok = await connect_and_write(addr_hint, payload)
        if ok: return

    # Otherwise/if failed: loop short scans until timeout, then connect
    deadline = time.monotonic() + total_timeout
    while time.monotonic() < deadline:
        dev = await discover_match(addr_hint, burst=4.0)
        if dev:
            if await connect_and_write(dev, payload): return
        # no match yet or connect failed; wait a bit and rescan
        await asyncio.sleep(0.8)

    raise RuntimeError("ESP32 not found / not connectable within timeout.")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].lower() not in ("on","off","1","0","true","false"):
        print("Usage: python ble_control.py [on|off] [optional_MAC_hint]")
        sys.exit(1)
    addr = sys.argv[2] if len(sys.argv) >= 3 else None
    asyncio.run(main(sys.argv[1], addr, total_timeout=20.0))
