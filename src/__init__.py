"""
This file registers the model with the Python SDK.
"""

from viam.components.sensor import Sensor
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .nova import nova

Registry.register_resource_creator(Sensor.SUBTYPE, nova.MODEL, ResourceCreatorRegistration(nova.new, nova.validate))
