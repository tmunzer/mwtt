from .device_event_common import CommonEvent


class ApEvent(CommonEvent):

    def __init__(self, mist_host, message_levels, event):
        CommonEvent.__init__(self, mist_host, message_levels, event)
        self.band = event.get("band", None)
        self.post_channel = event.get("channel", None)
        self.post_bandwidth = event.get("bandwidth", None)
        self.post_power = event.get("power", None)
        self.pre_channel = event.get("pre_channel", None)
        self.pre_bandwidth = event.get("pre_bandwidth", None)
        self.pre_power = event.get("pre_power", None)
        self.occurrence = event.get("occurrence", None)
        self.ssid = event.get("ssid", None)
        self.old_server = event.get("old_server", None)
        self.new_server = event.get("new_server", None)
        self.apfw = event.get("apfw", None)
        self.type_code = event.get("type_code", None)


    def _process(self):
        if self.event_type in ["AP_CLAIMED", "AP_UNCLAIMED"]:
            self._claimed()
        elif self.event_type == "AP_ASSIGNED":
            self._assigned()
        elif self.event_type == "AP_UNASSIGNED":
            self._unassigned()
        elif self.event_type == "AP_CONFIG_CHANGED_BY_RRM":
            self._ap_config_changed_by_rrm()
        elif self.event_type == "AP_CONFIG_CHANGED_BY_USER":
            self._config_changed_by_user()
        elif self.event_type == "AP_CONFIG_FAILED":
            self._config_failed()
        elif self.event_type in ["AP_CONFIGURED", "AP_RECONFIGURED"]:
            self._configured()
        elif self.event_type == "1026":
            self._ap_event_1026()
        elif self.event_type == "AP_RRM_ACTION":
            self._ap_rrm_action()
        elif self.event_type == "AP_BEACON_STUCK":
            self._ap_beacon_stuck()
        elif self.event_type == "AP_RADAR_DETECTED":
            self._ap_radar_detected()
        elif self.event_type == "AP_RESTART_BY_USER":
            self._restarted_by_user()
        elif self.event_type in ["AP_CONNECTED", "AP_DISCONNECTED"]:
            self._connected()
        elif self.event_type =="AP_RESTARTED":
            self._restarted()
        elif self.event_type == "AP_DISCONNECTED_LONG":
            self._disconnected_long()
        elif self.event_type == "AP_UPGRADE_BY_USER":
            self._upgrade_by_user()
        elif self.event_type == "AP_UPGRADED":
            self._upgraded()
        elif self.event_type == "AP_UPGRADE_BY_SCHEDULE":
            self._ap_upgraded_by_schedule()
        elif self.event_type == "AP_UPGRADE_BY_USER":
            self._upgrade_by_user()
        elif self.event_type == "AP_UPGRADE_FAILED":
            self._upgrade_failed()
        elif self.event_type == "AP_CERT_REGENERATED":
            self._cert_regenerated()
        elif self.event_type == "AP_GET_SUPPORT_FILES":
            self._ap_support_file()
        elif self.event_type in ["AP_RADIUS_ACCOUNTING_SERVER_CHANGE", "AP_RADIUS_AUTHENTICATION_SERVER_CHANGE"]:
            self._radius_server_change()
        elif self.event_type in ["AP_RADSEC_FAILURE", "AP_RADSEC_SERVER_CHANGE", "AP_RADSEC_RECOVERY"]:
            self._radsec()
        else:
            self._common()


    def _ap_config_changed_by_rrm(self):
        '''
{
    "type": "AP_CONFIGURED",
    "timestamp": 1552408871,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001"
}
        '''
        self.text = f"Configuration for AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""
        self.text += " changed by RRM."
        

    def _ap_event_1026(self):
        '''
    19/05/2020 00:21:04 INFO: device-events
    19/05/2020 00:21:04 INFO: ap: d420b0002e95
    19/05/2020 00:21:04 INFO: device_name: ap-41.off.lab
    19/05/2020 00:21:04 INFO: org_id: 203d3d02-dbc0-4c1b-9f41-76896a3330f4
    19/05/2020 00:21:04 INFO: reason: scheduled-site-rrm
    19/05/2020 00:21:04 INFO: site_id: fa018c13-008b-46ae-aa18-1eeb894a96c4
    19/05/2020 00:21:04 INFO: site_name: lab
    19/05/2020 00:21:04 INFO: timestamp: 1589847656
    19/05/2020 00:21:04 INFO: type: 1026
        '''
        self.text = f"Event 1026 for AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""

    def _ap_rrm_action(self):
        '''
{
    "type": "AP_RRM_ACTION",
    "timestamp": 1552408871,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001",
    "band": "5",
    "channel": 36,
    "bandwidth": 40,
    "power": 17,
    "pre_channel": 40,
    "pre_bandwidth": 40,
    "pre_power": 15,
    "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
    "reason": "radar-detected"
}
        '''
        self.text = f"RRM CHANGES in {self.band}GHz for the AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""
        self.info.append(f"*Channel*: {self.pre_channel} -> {self.post_channel}")
        self.info.append(f"*Bandwidth*: {self.pre_bandwidth}MHz -> {self.post_bandwidth}MHz")
        self.info.append(f"*Power*: {self.pre_power}dBm -> {self.post_power}dBm")

    def _ap_beacon_stuck(self):
        '''
{
    "type": "AP_BEACON_STUCK",
    "timestamp": 1552233041,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001",
    "band": "5",
    "start_time": 1552008073,
    "end_time": 1552232053,
    "occurrence": 747
}
        '''
        self.text = f"{self.occurrence} BEANCON STUCK in {self.band}GHz for the AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""


    def _ap_radar_detected(self):
        '''
{
    "type": "AP_RADAR_DETECTED",
    "timestamp": 1552233041,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001",
    "band": "5",
    "channel": 36,
    "bandwidth": 40,
    "pre_channel": 125,
    "pre_bandwidth": 40,
    "reason": "radar-detected"
}
        '''
        self.text = f"RADAR DETECTED on channel {self.pre_channel}/{self.pre_bandwidth}MHz by the AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""
        self.info.append(f"*Channel*: {self.pre_channel} -> {self.post_channel}")
        self.info.append(f"*Bandwidth*: {self.pre_bandwidth}MHz -> {self.post_bandwidth}MHz")
        self.info.append(f"*Power*: {self.pre_power}dBm -> {self.post_power}dBm")

    def _ap_upgraded_by_schedule(self):
        '''
{
    "type": "AP_UPGRADE_BY_SCHEDULE",
    "timestamp": 1552408871,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001"
}
        '''
        self.text = f"AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""
        self.text += " UPGRADED BY SCHEDULE POLICY"

    def _ap_support_file(self):
        '''
{
    "type": "AP_GET_SUPPORT_FILES",
    "timestamp": 1552233041,
    "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
    "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
    "ap": "5c5b35000001",
    "device_type": "ap"
}
        '''
        self.text = f"SUPPORT FILE RETRIEVED for AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""

    def _radius_server_change(self):
        '''
        {
            "org_id": "442f2ff3-b121-40ff-9443-d753ab96463c",
            "site_id": "2e28d07a-ac92-435c-bad8-3cddba3d9b17",
            "wlan_id": "7d88910f-bfd6-47b6-883a-db8f91bae74c",
            "type": "AP_RADIUS_ACCOUNTING_SERVER_CHANGE",
            "old_server": "7.7.7.7:8888",
            "new_server": "1.2.3.5:1235",
            "ssid": "RADIUS_TEST",
            "ap": "d420b0f1030c",
            "timestamp": 1651515384
        }
        '''
        tmp = self.event_type.replace("AP_", "").replace("_", " ")
        self.text  = f"{tmp} for SSID \"{self.ssid}\" from {self.old_server} to {self.new_server}"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""

    def _radsec(self):
        '''
{
            "wlan_id": "b19ce109-1f86-4d9b-bdff-19a08d94655d",
            "type": "AP_RADSEC_FAILURE",
            "device_type": "ap",
            "version": 1,
            "apfw": "0.12.26260",
            "mac": "d420b0f1030c",
            "ap": "d420b0f1030c",
            "timestamp": 1654148714.073,
            "org_id": "442f2ff3-b121-40ff-9443-d753ab96463c",
            "site_id": "2e28d07a-ac92-435c-bad8-3cddba3d9b17",
            "model": "AP45-US",
            "text": "Radsec client cert format error",
            "type_code": 38
        }
        {
            "wlan_id": "06dac5f2-a8b9-4e56-872e-cd1c1d55267c",
            "type": "AP_RADSEC_SERVER_CHANGE",
            "device_type": "ap",
            "version": 1,
            "apfw": "apfw-0.12.26260-lollys-ca00",
            "ap": "d420b0f103e8",
            "mac": "d420b0f103e8",
            "timestamp": 1654148714.073,
            "org_id": "f2695c32-0e83-4936-b1b2-96fc88051213",
            "site_id": "85d94e1f-3629-46b9-85f8-a760499005cf",
            "model": "AP45-US",
            "text": "Using Radsec server \"1.1.1.222:2083\"",
            "type_code": 52
        }
        {
            "wlan_id": "983c8169-25fe-455c-a62a-5cac1224607e",
            "type": "AP_RADSEC_RECOVERY",
            "device_type": "ap",
            "version": 1,
            "apfw": "apfw-0.6.19227-frey-ab55",
            "ap": "5c5b355005be",
            "mac": "5c5b355005be",
            "timestamp": 1654148714.073,
            "org_id": "625aba64-fe72-4b14-8985-cbf31ec3d78a",
            "site_id": "ec9d1e85-af24-43f9-8d65-d620580e8631",
            "model": "AP43-US",
            "text": "TLS established successfully with radsec server \"a268dc897b17c4c08af1eba3118580c3-8c2ed33f47d43bad.elb.us-west-2.amazonaws.com:2083\" (10.2.17.224:57276->52.27.123.97:2083)",
            "type_code": 59
        }
        '''
        tmp = self.event_type.replace("AP_", "").replace("_", " ")
        self.text  = f"{tmp} for AP \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""
        self.info.append(f"*AP Firmware*: {self.apfw}")
        self.info.append(f"*AP Model*: {self.model}")
        self.info.append(f"*Details*: {self.event_text}")
        self.info.append(f"*Code*: {self.type_code}")