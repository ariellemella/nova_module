import asyncio
import sys

from viam.components.sensor import Sensor
from viam.module.module import Module
from .nova import nova

async def main(address: str):
    module = Module(address)
    module.add_model_from_registry(Sensor.SUBTYPE, nova.MODEL)
    await module.start()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Need socket path as command line argument")

    asyncio.run(main(sys.argv[1]))
