import struct

from typing import ClassVar, Mapping, Sequence, Any, Dict, Optional, cast
from typing_extensions import Self

from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, Vector3
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily

from viam.components.sensor import Sensor
from viam.logging import getLogger

import time
import asyncio

LOGGER = getLogger(__name__)

class nova(Sensor, Reconfigurable):
    HEAD = b'\xaa'
    TAIL = b'\xab'
    CMD_ID = b'\xb4'

    # The sent command is a read or a write
    READ = b"\x00"
    WRITE = b"\x01"

    REPORT_MODE_CMD = b"\x02"
    ACTIVE = b"\x00"
    PASSIVE = b"\x01"

    QUERY_CMD = b"\x04"

    # The sleep command ID
    SLEEP_CMD = b"\x06"
    # Sleep and work byte
    SLEEP = b"\x00"
    WORK = b"\x01"

    # The work period command ID
    WORK_PERIOD_CMD = b'\x08'

    usb_path = "/dev/ttyUSB0"

    MODEL: ClassVar[Model] = Model(ModelFamily("viamlabs", "sensor"), "nova")

    # Constructor
    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    # Validates JSON Configuration
    @classmethod
    def validate(cls, config: ComponentConfig):
        # here we validate config, the following is just an example and should be updated as needed
        usb_path = config.attributes.fields["usb_path"]
        if usb_path == "":
            raise Exception("A usb_path must be defined")
        return

    # Handles attribute reconfiguration
    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        # here we initialize the resource instance, the following is just an example and should be updated as needed
        self.usb_path = int(config.attributes.fields["usb_path"])
        return

    """ Implement the methods the Viam RDK defines for the Sensor API (rdk:components:sensor) """

    
    # async def get_readings(
    #     self, *, extra: Optional[Mapping[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    # ) -> Mapping[str, Any]:
    #     """
    #     Obtain the measurements/data specific to this sensor.

    #     Returns:
    #         Mapping[str, Any]: The measurements. Can be of any type.
    #     """
    #     ...

    async def _process_frame(self, data):
        """Process a SDS011 data frame.

        Byte positions:
            0 - Header
            1 - Command No.
            2,3 - PM2.5 low/high byte
            4,5 - PM10 low/high
            6,7 - ID bytes
            8 - Checksum - sum of bytes 2-7
            9 - Tail
        """
        raw = struct.unpack('<HHxxBBB', data[2:])
        checksum = sum(v for v in data[2:8]) % 256
        if checksum != data[8]:
            return None
        pm25 = raw[0] / 10.0
        pm10 = raw[1] / 10.0
        return (pm25, pm10)


    async def get_readings(self):
        byte = 0
        while byte != self.HEAD:
            byte = self.ser.read(size=1)
            d = self.ser.read(size=10)
            if d[0:1] == b"\xc0":
                data = self._process_frame(byte + d)
                return data
