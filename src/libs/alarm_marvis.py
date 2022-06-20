from datetime import datetime
from .alarm_common import CommonAlarm


class MarvisAlarm(CommonAlarm):

    def __init__(self, mist_host, alarm_channels, event):
        CommonAlarm.__init__(self, mist_host, alarm_channels, event)
        self.group = "marvis"
        self.status = event.get("status", "Unknown")
        self.category = event.get("category")
        self.root_cause = event.get("root_case")
        self.suggestion = event.get("suggestion", "Unknown")
        self.impacted_entities = event.get("impacted_entities", [])


    def _process(self):
        if self.alarm_type in [
            "missing_vlan",
            "bad_cable", "gw_bad_cable", "ap_bad_cable",
            "authentication_failure", "dhcp_failure", "arp_failure", "dns_failure",
            "port_flap",
            "negotiation_mismatch", "gw_negotiation_mismatch",
            "ap_offline",
            "non_compliant",
            "health_check_failed",
            "bad_wan_uplink",
            "switch_stp_loop",
            "insufficient_coverage",
            "insufficient_capacity"
        ]:
            self._marvis()
        else:
            self._common()

    def _marvis(self):
        """
        """
        self.text = f"MARVIS {self.alarm_type.replace('_', ' ').upper()} issue on site {self.site_name}"
        
        self.info.append(f"*STATUS*: {self.status}")
        if self.category:
            self.info.append(f"*CATEGORY*: {self.category}")
        if self.root_cause:
            self.info.append(f"*ROOT CAUSE*: {self.root_cause}")
        if self.suggestion:
            self.info.append(f"*SUGGESTION*: {self.suggestion}")
        self.info.append(f"*IMPACTED ENTITIES:* {len(self.impacted_entities)}")
        for entry in self.impacted_entities:
            tmp = ""
            for key in entry:
                tmp += f"\r\n> {key.replace('_', ' ')}: {entry[key]}"
            self.info.append(tmp)