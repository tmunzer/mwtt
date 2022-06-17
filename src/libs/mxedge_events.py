from .device_event_common import CommonEvent

def mxedge_event(mist_host, message_levels, mist_event):
    return MxEdgeEvent(mist_host, message_levels, mist_event).get()
    


class MxEdgeEvent(CommonEvent):

    def __init__(self, mist_host, message_levels, event):
        CommonEvent.__init__(self, mist_host, message_levels, event)
        event["device_id"] = event["mxedge_id"]
        self.device_type = "mxedge"
        self.device_text = "Mist Edge"
        self.device_name = event.get("mxedge_name")
        self.device_id =event.get("mxedge_id")
        self.package =event.get("package")
        self.from_version =event.get("from_version")
        self.to_version =event.get("to_version")
        self.bounced_ports =event.get("bounced_ports", [])
        self.disconnected_aps =event.get("disconnected_aps", [])
        self.component =event.get("component", "Unknown")
        self.port =event.get("port", "Unknown")
        self.lag =event.get("lag", "Unknown")
        if "usage" in event:
            self.severity = event["usage"].get("severity")
            self.resource = event["usage"].get("resource")
        elif "sys_info.usage" in event:
            self.severity = event["sys_info.usage"].get("severity")
            self.resource = event["sys_info.usage"].get("resource")
        else:
            self.severity = "Unknown"
            self.resource = "Unknown"


        self.device_mac = self.device_id.split('-')[4]
        self.cluster_id = event.get("mxcluster_id")
        self.service = event.get("service")
        if event.get("sys_info", {}).get("usage"):
            self.usage = {
                "severity" : f'{event["sys_info"]["usage"].get("high", "Unknown")}'.upper(),
                "threshold_value" : f'{event["sys_info"]["usage"].get("threshold_value", "Unknown")}',
                "actual_value" : f'{event["sys_info"]["usage"].get("actual_value", "Unknown")}',
                "resource" : f'{event["sys_info"]["usage"].get("resource", "Unknown")}'.upper()
            }

    def _actions(self):
        if "audit_id" in self.event:
            url_audit = f"https://{self.mist_dashboard}/admin/?org_id={self.org_id}#!auditLogs"
            self.actions.append(
                {"tag": "audit", "text": "Audit Logs", "url": url_audit})
        if self.device_id and self.device_id.startswith("00000000-0000-0000-1000"):
            url_insights = f"https://{self.mist_dashboard}/admin/?org_id={self.org_id}#!dashboard/insights/edge/{self.device_id}/24h/{self.t_start}/{self.t_stop}/{self.site_id}"
            self.actions.append({
                "tag": "insights",
                "text": "Edge Insights",
                "url": url_insights
            })
            url_conf = f"https://{self.mist_dashboard}/admin/?org_id={self.org_id}#!edge/edgedetail/{self.device_id}"
            self.actions.append({
                "tag": "insights",
                "text": "Edge Configuration",
                "url": url_conf
            })
        if self.cluster_id:
            url_conf = f"https://{self.mist_dashboard}/admin/?org_id={self.org_id}#!edge/clusterdetail/{self.cluster_id}"
            self.actions.append({
                "tag": "insights",
                "text": "Cluster Configuration",
                "url": url_conf
            })

    def _process(self):
        if self.event_type == "ME_CONFIG_CHANGED_BY_USER":
            self._me_config_changed_by_user()       
        elif self.event_type in ["ME_SERVICE_STOPPED", "ME_SERVICE_STARTED", "ME_SERVICE_RESTARTED", "ME_SERVICE_FAILED", "ME_SERVICE_CRASHED"]:
            self._me_service()
        elif self.event_type == "TT_TUNNELS_LOST":
            self._me_tunnel()
        elif self.event_type in ["ME_PACKAGE_INSTALLED", "ME_PACKAGE_UNINSTALLED","ME_PACKAGE_INSTALL_FAILED", "ME_PACKAGE_UNINSTALL_FAILED" ]:
            self._me_package()
        elif self.event_type in ["ME_PACKAGE_UPDATED", "ME_PACKAGE_UPDATE_BY_USER"]:
            self._me_package_update()
        elif self.event_type in ["ME_PACKAGE_UPDATE_FAILED"]:
            self._me_package_update_failed()
        elif self.event_type == "ME_RESTARTED":
            self._restarted()
        elif self.event_type == "ME_RESOURCE_USAGE":
            self._me_resources()
        elif self.event_type == "ME_CONFIGURED":
            self._configured()
        elif self.event_type == "ME_RESTART_BY_USER":
            self._restarted_by_user()
        elif self.event_type in ["ME_CONNECTED", "ME_DISCONNECTED"]:
            self._connected()
        elif self.event_type in ["TT_PORT_BLOCKED", "TT_PORT_RECOVERY", "TT_PORT_LINK_DOWN", "TT_PORT_LINK_RECOVERY"]:
            self._me_port()
        elif self.event_type in ["TT_PORT_DROPPED_FROM_LACP", "TT_PORT_JOINED_LACP"]:
            self._me_port_lacp()
        elif self.event_type in ["TT_PORTS_BOUNCE_BY_USER", "TT_PORTS_BOUNCED", "TT_PORTS_BOUNCE_FAILED"]:
            self._me_port_bounce()
        elif self.event_type in ["TT_AP_DISCONNECT_BY_USER", "TT_AP_DISCONNECTED", "TT_AP_DISCONNECT_FAILED"]:
            self._me_ap_disconnect()
        elif self.event_type in ["ME_FAN_PLUGGED", "ME_FAN_UNPLUGGED", "ME_PSU_PLUGGED", "ME_PSU_UNPLUGGED", "ME_POWERINPUT_CONNECTED", "ME_POWERINPUT_DISCONNECTED"]:
            self._me_hardware()
        else:
            self._common()

    def _me_config_changed_by_user(self):
        '''
        {
            "audit_id": "8682cd17-189f-4ced-a21d-a1e1e93dbb9b",
            "mxcluster_id": "526ef8aa-4721-4f03-99cf-7ac4560577f7",
            "mxedge_id": "00000000-0000-0000-1000-020000ee2974",
            "mxedge_name": "mxe-ex",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "timestamp": "1655391344.807150",
            "type": "ME_CONFIG_CHANGED_BY_USER"
        },
        {
            "audit_id": "8682cd17-189f-4ced-a21d-a1e1e93dbb9b",
            "mxcluster_id": "526ef8aa-4721-4f03-99cf-7ac4560577f7",
            "mxedge_id": "72038044-7045-48a4-a718-064a8f6d08d7",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "timestamp": "1655391344.810688",
            "type": "ME_CONFIG_CHANGED_BY_USER"
        }
        '''
        self.text = f"Mist Edge CONFIGURATION CHANGED by user"
        if self.device_id and self.device_id.startswith("00000000-0000-0000-1000"):
            self.text += f" on \"{self.device_name}\" (MAC: {self.device_mac})"
        if self.site_name:
            self.text += f" on site \"{self.site_name}\""

    def _me_service(self):
        '''
        {
            "mxcluster_id": "6d0f7305-51fd-4eed-9447-5282e1ac835e",
            "mxedge_id": "00000000-0000-0000-1000-020000958f4f",
            "mxedge_name": "mxe-02",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "service": "tunterm",
            "timestamp": "1655176859.081000",
            "type": "ME_SERVICE_RESTARTED"
        },
        {
            "mxcluster_id": "6d0f7305-51fd-4eed-9447-5282e1ac835e",
            "mxedge_id": "00000000-0000-0000-1000-020000958f4f",
            "mxedge_name": "mxe-02",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "service": "tunterm",
            "timestamp": "1655176871.080000",
            "type": "ME_SERVICE_FAILED"
        },
        {
            "mxcluster_id": "6d0f7305-51fd-4eed-9447-5282e1ac835e",
            "mxedge_id": "00000000-0000-0000-1000-020000958f4f",
            "mxedge_name": "mxe-02",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "service": "tunterm",
            "timestamp": "1655176841.007000",
            "type": "ME_SERVICE_STARTED"
        },
    {
            "mxcluster_id": "526ef8aa-4721-4f03-99cf-7ac4560577f7",
            "mxedge_id": "00000000-0000-0000-1000-020000ee2974",
            "mxedge_name": "mxe-ex",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "service": "tunterm",
            "timestamp": "1655035012.182000",
            "type": "ME_SERVICE_STOPPED"
            }
            {
            "type": "ME_SERVICE_CRASHED",
            "service": "tunterm",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90"
        }
        '''
        self.text = f"SERVICE {self.service}"
        tmp = self.event_type.split("_")
        self.text += f" {tmp[len(tmp)-1]}"
        self.text += f" on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_tunnel(self):
        '''
        {
            "mxcluster_id": "526ef8aa-4721-4f03-99cf-7ac4560577f7",
            "mxedge_id": "00000000-0000-0000-1000-020000ee2974",
            "mxedge_name": "mxe-ex",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "timestamp": "1655038573.031481",
            "type": "TT_TUNNELS_LOST"
        }
        '''
        tmp = self.event_type.replace("TT", "TUNTERM").replace("_", " ")
        self.text += f"{tmp} on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_port(self):
        """
{
            "type": "TT_PORT_BLOCKED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "port": "port0"
        }
        {
            "type": "TT_PORT_RECOVERY",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "port": "port0"
        }
        {
            "type": "TT_PORT_LINK_DOWN",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "port": "port0"
        }{
            "type": "TT_PORT_LINK_RECOVERY",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "port": "port0"
        }
        """
        tmp = self.event_type.replace("TT_PORT_", "").replace("_", " ")
        self.text = f"TUNTERM PORT {self.port} {tmp} on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_port_bounce(self):
        """
        {
            "type": "TT_PORTS_BOUNCE_BY_USER",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "bounced_ports": [
                "0",
                "2"
            ]
        }
        {
            "type": "TT_PORTS_BOUNCED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "bounced_ports": [
                "0",
                "2"
            ]
        }{
            "type": "TT_PORTS_BOUNCE_FAILED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "bounced_ports": [
                "0",
                "2"
            ]
        }
        """

        tmp = self.event_type.replace("TT", "TUNTERM").replace("_", " ")
        self.text = f"{tmp} on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""
        if len(self.bounced_ports) > 0:
            self.text += f" for ports {', '.join(self.bounced_ports)}"


    def _me_port_lacp(self):
        """
        {
            "type": "TT_PORT_DROPPED_FROM_LACP",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "lag": "lacp0",
            "port": "port0"
        }
        {
            "type": "TT_PORT_JOINED_LACP",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "lag": "lacp0",
            "port": "port0"
        }
        """
        tmp = self.event_type.replace("TT_PORT_", "").replace("_", " ")
        self.text = f"TUNTERM PORT {self.port} {tmp} from LAG {self.lag} on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_ap_disconnect(self):
        """
{
            "type": "TT_AP_DISCONNECT_BY_USER",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "disconnected_aps": [
                "5c-5b-35-3e-4e-b1"
            ]
        }{
            "type": "TT_AP_DISCONNECTED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "disconnected_aps": [
                "5c-5b-35-3e-4e-b1"
            ]
        }{
            "type": "TT_AP_DISCONNECT_FAILED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5",
            "disconnected_aps": [
                "5c-5b-35-3e-4e-b1"
            ]
        }
        """

        tmp = self.event_type.replace("TT", "TUNTERM").replace("_", " ")
        self.text = f"{tmp} on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""
        if len(self.bounced_ports) > 0:
            self.text += f" for APs {', '.join(self.disconnected_aps)}"
    def _me_package(self):
        '''
 {
            "type": "ME_PACKAGE_INSTALLED",
            "package": "tunterm",
            "to_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
    }
    {
            "type": "ME_PACKAGE_UNINSTALLED",
            "package": "tunterm",
            "from_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
{
            "type": "ME_PACKAGE_INSTALL_FAILED",
            "package": "tunterm",
            "to_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
    {
            "type": "ME_PACKAGE_UNINSTALL_FAILED",
            "package": "tunterm",
            "from_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
        '''
        self.text = f"Mist Edge package {self.package}"
        if self.to_version:
            self.text += f" {self.to_version}"
        elif self.from_version:
            self.text += f" {self.from_version}"
        tmp = self.event_type.replace("ME_PACKAGE_", "").replace("_", " ")
        self.text += f" {tmp}"
        if self.device_name:
            self.text += f" on \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_package_update(self):
        '''
        {
            "type": "ME_PACKAGE_UPDATED",
            "package": "tunterm",
            "from_version": "0.1.1906+deb9",
            "to_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
        {
            "type": "ME_PACKAGE_UPDATE_BY_USER",
            "package": "tunterm",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
        '''
        tmp = self.event_type.replace("ME_PACKAGE_", "").replace("_", " ")
        self.text = f"Mist Edge package {self.package} {tmp}"
        if self.from_version:
            self.text += f"from {self.from_version}"
        if self.to_version:
            self.text += f"to {self.to_version}"
        if self.device_name:
            self.text += f" on \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_package_update_failed(self):
        '''
        {
            "type": "ME_PACKAGE_UPDATE_FAILED",
            "package": "tunterm",
            "from_version": "0.1.1906+deb9",
            "to_version": "0.1.1907+deb9",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "audit_id": "e9a88814-fa81-5bdc-34b0-84e8735420e5"
        }
        '''
        self.text = f"Mist Edge UPDATED FAILED for package {self.package}"
        if self.from_version:
            self.text += f"from {self.from_version}"
        if self.to_version:
            self.text += f"to {self.to_version}"
        if self.device_name:
            self.text += f" on \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _me_resources(self):
        '''
         {
            "mxcluster_id": "526ef8aa-4721-4f03-99cf-7ac4560577f7",
            "mxedge_id": "00000000-0000-0000-1000-020000ee2974",
            "mxedge_name": "mxe-ex",
            "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
            "sys_info": {
                "usage": {
                    "actual_value": 65.06659864741566,
                    "resource": "memory",
                    "severity": "normal",
                    "threshold_value": 70
                }
            },
            "timestamp": "1655186366.894000",
            "type": "ME_RESOURCE_USAGE"
        }
        '''
        self.text = f"{self.resource} usage on Mist Edge \"{self.device_name}\" is {self.severity}"
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""


    def _me_hardware(self):
        """
        {
            "type": "ME_FAN_PLUGGED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "Fan1",
            "severity": "normal"
        }
        {
            "type": "ME_FAN_UNPLUGGED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "Fan1",
            "severity": "critical"
        }
        {
            "type": "ME_PSU_PLUGGED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "PS1",
            "severity": "normal"
        }
        {
            "type": "ME_PSU_UNPLUGGED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "PS1",
            "severity": "critical"
        }
        {
            "type": "ME_POWERINPUT_CONNECTED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "PS1",
            "severity": "normal"
        }
        {
            "type": "ME_POWERINPUT_DISCONNECTED",
            "timestamp": 1552408871,
            "org_id": "2818e386-8dec-2562-9ede-5b8a0fbbdc71",
            "site_id": "4ac1dcf4-9d8b-7211-65c4-057819f0862b",
            "mxcluster_id": "ed4665ed-c9ad-4835-8ca5-dda642765ad3",
            "mxedge_id": "387804a7-3474-85ce-15a2-f9a9684c9c90",
            "component": "PS1",
            "severity": "critical"
        }
        """
        tmp = self.event_type.replace("ME_", "").split("_")
        self.text = f"Mist Edge {tmp[0]} \"{self.component}\" {tmp[1]}"
        if self.device_name:
            self.text += f" on \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""