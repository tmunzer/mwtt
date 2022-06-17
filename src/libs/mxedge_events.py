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
        elif self.event_type in ["ME_SERVICE_STOPPED", "ME_SERVICE_STARTED", "ME_SERVICE_RESTARTED", "ME_SERVICE_FAILED"]:
            self._service()
        elif self.event_type == "TT_TUNNELS_LOST":
            self._tunnel()
        elif self.event_type in ["ME_PACKAGE_INSTALLED", "ME_PACKAGE_UPDATE_BY_USER"]:
            self._package()
        elif self.event_type == "ME_RESTARTED":
            self._restarted()
        elif self.event_type == "ME_RESOURCE_USAGE":
            self._resources()
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

    def _service(self):
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
        '''
        self.text = f"Service {self.service}"
        tmp = self.event_type.split("_")
        self.text += f" {tmp[len(tmp)-1]}"
        self.text += f" on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _tunnel(self):
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
        self.text = "Tunnel"
        tmp = self.event_type.split("_")
        self.text += f" {tmp[len(tmp)-1]}"
        self.text += f" on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _package(self):
        '''
        {
                "mxedge_id": "00000000-0000-0000-1000-020000ee2974",
                "mxedge_name": "mxe-ex",
                "org_id": "203d3d02-dbc0-4c1b-9f41-76896a3330f4",
                "package": "tunterm",
                "timestamp": "1655030856.269000",
                "type": "ME_PACKAGE_INSTALLED"
            }
        '''
        self.text = "Package"
        tmp = self.event_type.replace("ME_PACKAGE", "").replace("_", " ")
        self.text += f" {tmp}"
        self.text += f" on Mist Edge \"{self.device_name}\""
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""

    def _resources(self):
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
        self.text += f"{self.usage['resource']} usage on Mist Edge \"{self.device_name}\" is {self.usage['severity']}"
        if self.site_name:
            self.text +=  f" on site \"{self.site_name}\""