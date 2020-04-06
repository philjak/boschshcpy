from enum import Enum

from .device import SHCDevice
from .device_service import SHCDeviceService
from .services_impl import ShutterContactService, ShutterControlService, CameraLightService, IntrusionDetectionControlService


class SHCSmokeDetector(SHCDevice):
    from .services_impl import AlarmService, SmokeDetectorCheckService

    class AlarmState(Enum):
        INTRUSION_ALARM_ON_REQUESTED = "INTRUSION_ALARM_ON_REQUESTED"
        INTRUSION_ALARM_OFF_REQUESTED = "INTRUSION_ALARM_OFF_REQUESTED"
        MUTE_SECONDARY_ALARM_REQUESTED = "MUTE_SECONDARY_ALARM_REQUESTED"

    def __init__(self, api, raw_device):
        super().__init__(api, raw_device)

        self._alarm_service: AlarmService = self.device_service('Alarm')
        self._smokedetectorcheck_service: SmokeDetectorCheckService = self.device_service(
            'SmokeDetectorCheck')

    def set_alarmstate(self, state: AlarmState):
        self._alarm_service.put_state_element('state', state.name)

    @property
    def alarm_state(self) -> AlarmService.State:
        return self._alarm_service.value

    @property
    def smokedetectorcheck_state(self) -> SmokeDetectorCheckService.State:
        return self._smokedetectorcheck_service.value

    def update(self):
        self._alarm_service.short_poll()
        self._smokedetectorcheck_service.short_poll()

    def summary(self):
        print(f"SD SmokeDetector:")
        super().summary()


class SHCSmartPlug(SHCDevice):
    def __init__(self, api, raw_device):
        super().__init__(api, raw_device)

        self._service = self.device_service('PowerSwitch')

    def set_state(self, state: bool):
        self._service.put_state_element('state', state)

    def summary(self):
        print(f"PSM SmartPlug:")
        super().summary()


class SHCShutterControl(SHCDevice):
    from .services_impl import ShutterControlService

    def __init__(self, api, raw_device):
        super().__init__(api, raw_device=raw_device)
        self._service: ShutterControlService = self.device_service('ShutterControl')

    def set_level(self, level):
        self._service.put_state_element('level', level)

    @property
    def level(self) -> float:
        return self._service.level

    def set_stopped(self):
        self._service.put_state_element('operationState', ShutterControlService.State.STOPPED.name)

    @property
    def operation_state(self) -> ShutterControlService.State:
        return self._service.value

    def update(self):
        self._service.short_poll()

    def summary(self):
        print(f"BBL ShutterControl:")
        super().summary()


class SHCShutterContact(SHCDevice):
    from .services_impl import ShutterContactService
    class DeviceClass(Enum):
        GENERIC = "GENERIC"
        ENTRANCE_DOOR = "ENTRANCE_DOOR"
        REGULAR_WINDOW = "REGULAR_WINDOW"
        FRENCH_WINDOW = "FRENCH_WINDOW"

    def __init__(self, api, raw_device):
        super().__init__(api, raw_device)
        self._service = self.device_service('ShutterContact')

    @property
    def device_class(self) -> DeviceClass:
        return self.DeviceClass(self.profile)

    @property
    def state(self) -> ShutterContactService.State:
        return self._service.value

    def update(self):
        self._service.short_poll()

    def summary(self):
        print(f"SWD ShutterContact:")
        super().summary()


class SHCCameraEyes(SHCDevice):
    def __init__(self, api, raw_device):
        super().__init__(api, raw_device)

        self._privacymode_service = self.device_service('PrivacyMode')
        self._cameranotification_service = self.device_service(
            'CameraNotification')
        self._cameralight_service = self.device_service('CameraLight')

    def set_privacymode(self, state: bool):
        self._privacymode_service.put_state_element(
            'value', "ENABLED" if state else "DISABLED")

    def set_cameranotification(self, state: bool):
        self._cameranotification_service.put_state_element(
            'value', "ENABLED" if state else "DISABLED")

    def set_cameralight(self, state: bool):
        self._cameralight_service.put_state_element(
            'value', "ON" if state else "OFF")

    @property
    def lightstate(self) -> CameraLightService.State:
        self._cameralight_service.short_poll()
        return self._cameralight_service.value

    def summary(self):
        print(f"CAMERA_EYES CameraEyes:")
        super().summary()


class SHCIntrusionDetectionSystem(SHCDevice):
    def __init__(self, api, raw_device):
        super().__init__(api, raw_device)
        self._service = self.device_service('IntrusionDetectionControl')

    def set_alarmstate(self, state: IntrusionDetectionControlService.State):
        self._service.put_state_element('value', state.name)

    def disarm(self):
        self.set_alarmstate(IntrusionDetectionControlService.State.SYSTEM_DISARMED)

    def arm(self):
        self.set_alarmstate(IntrusionDetectionControlService.State.SYSTEM_ARMED)

    def arm_activation_delay(self, seconds):
        if self.alarmstate == IntrusionDetectionControlService.State.SYSTEM_ARMING:
            return

        self._service.put_state_element('armActivationDelayTime', seconds)

    def arm_instant(self):
        if self.alarmstate == IntrusionDetectionControlService.State.SYSTEM_ARMING:
            return

        delay_time = self._service.armActivationDelayTime
        self.arm_activation_delay(1)
        self.arm()
        self.arm_activation_delay(delay_time)

    def mute_alarm(self):
        self.set_alarmstate(IntrusionDetectionControlService.State.MUTE_ALARM)

    def trigger(self):
        # not implemented yet
        print("Trigger alarm simulation")

    @property
    def alarmstate(self) -> IntrusionDetectionControlService.State:
        self._service.short_poll()
        return self._service.value

    @property
    def armActivationDelayTime(self):
        self._service.short_poll()
        return self._service.value

    def summary(self):
        print(f"-IntrusionDetectionSystem-:")
        super().summary()


MODEL_MAPPING = {
    "SWD": "ShutterContact",
    "BBL": "ShutterControl",
    "PSM": "SmartPlug",
    "SD": "SmokeDetector",
    "CAMERA_EYES": "CameraEyes",
    "INTRUSION_DETECTION_SYSTEM": "-IntrusionDetectionSystem-"
}
# "WRC2": "UniversalSwitchFlex",
# "BSM": "LightControl",
# "MD": "MotionDetector"

SUPPORTED_MODELS = MODEL_MAPPING.keys()