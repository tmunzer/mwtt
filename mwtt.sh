#!/bin/bash

# =========================================================
# =========================================================
#
#            SYSTEM PARAMETERS
#            DO NOT CHANGE!!!
#
# =========================================================
# =========================================================
SCRIPT_CONF=`pwd`"/mist-docker.conf"
SCRIPT_NAME="mwtt.py"

APP_NAME="mwtt"
APP_IMG="tmunzer/mwtt"

# =========================================================
# NGINX server configuration
# true if email server is needed by the App

NGINX_CERTS_FOLDER="certs"
NGINX_NAME="mist-proxy"
NGINX_IMG="jwilder/nginx-proxy"


DOCKER=""
DOCKER_COMP=""

# =========================================================
# Colors
INFOC='\033[0;32m'
WARNINGC='\033[0;33m'
ERRORC='\033[0;31m'
NC='\033[0m' # No Color

################################################################################
############################    BANNER
################################################################################
function banner
{
  echo ""
  echo "||============================================================================="
  echo "||"
  echo "||       $1"
  echo "||"
  echo "||============================================================================="
}

################################################################################
############################    FILE GENERATORS
################################################################################

function generate_docker_compose_ngninx # $XX_NAME
{
  if [ ! -f $PERSISTANT_FOLDER/$APP_NAME/docker-compose.nginx.yaml ]
  then 
    cat <<EOF > $PERSISTANT_FOLDER/$APP_NAME/docker-compose.nginx.yaml
version: '3.5'
services:    
    nginx:
        image: "jwilder/nginx-proxy:1.2.3"
        container_name: "mist-nginx"
        ports:
            - "443:443"
        volumes:
            - $NGINX_CERTS_FOLDER:/etc/nginx/certs:ro  
            - /var/run/docker.sock:/tmp/docker.sock:ro        
            - /etc/nginx/vhost.d
        restart: always
        networks:
            - mist-net-nginx


networks:
    mist-net-nginx:
        driver: bridge
        name: mist-net-nginx
EOF
  fi
}
function generate_docker_compose_mongodb # $XX_NAME
{
  if [ ! -f $PERSISTANT_FOLDER/$APP_NAME/docker-compose.mongodb.yaml ]
  then 
    cat <<EOF > $PERSISTANT_FOLDER/$APP_NAME/docker-compose.mongodb.yaml
version: '3.5'
services:    
    mongodb:
        image: "mongo"
        container_name: "mist-mongodb"
        restart: always
        volumes: 
            - $MONGO_FOLDER:/data/db
        networks:
            - mist-net-mongodb

networks:
    mist-net-mongodb:
        driver: bridge
        name: mist-net-mongodb

EOF
  fi
}
function generate_docker_compose_app # $XX_NAME
{
  if [ ! -f $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml ]
  then 
    cat <<EOF > $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml
version: '3.5'
services:    
    $APP_NAME: 
        image: $APP_IMG
        container_name: "mist-$APP_NAME"
        external_links: 
            - nginx
        environment:
            - VIRTUAL_HOST=$APP_VHOST
        volumes:
            - $PERSISTANT_FOLDER/$APP_NAME/config.py:/app/config.py:ro         
        networks:            
            - mist-net-nginx
networks:
  mist-net-nginx:
    name: mist-net-nginx
EOF
  fi
}


function generate_conf_file # $XX_NAME
{
  if [ ! -f $PERSISTANT_FOLDER/$APP_NAME/config.py ]
  then 
    echo -e "${WARNINGC}WARNING${NC}:This script will automatically generate a default configuration"
    echo -e "         but you'll have to configure it before starting the app."
    echo ""
    echo -e "         File location: $PERSISTANT_FOLDER/$APP_NAME/config.py"
    echo ""
    touch $PERSISTANT_FOLDER/$APP_NAME/config.py
    cat <<\EOF > $PERSISTANT_FOLDER/$APP_NAME/config.py

########################
# mist_conf:
# Configuration to receive webhooks from Mist Cloud and to send API
# requests to Mist Cloud
#
# server_uri:       uri where you want to receive wehbooks messages
#                   on this server.
# mist_secret:      the webhook secret configuration on the Mist Cloud
#                   to secure webhook reception
mist_conf = {
    "mist_secret": None,
    "server_uri": "/webhooks",
    "site_id_ignored": [],
    "approved_admins": ["user@domain.com"]
}

log_level = "INFO"
# You can create more slack / msteams channel urls depending on your needs, you just need to be sure each
# channel has a unique name
slack_conf = {
    "enabled": True,
    "default_url": "https://hooks.slack.com/services/XXXXXXXX/XXXXXXXXX/XXXXXXXXXXX4",
    "url": {
        "debug": "https://hooks.slack.com/services/XXXXXXXX/XXXXXXXXX/XXXXXXXXXXX1",
        "info": "https://hooks.slack.com/services/XXXXXXXX/XXXXXXXXX/XXXXXXXXXXX2",
        "warning": "https://hooks.slack.com/services/XXXXXXXX/XXXXXXXXX/XXXXXXXXXXX3",
        "critical": "https://hooks.slack.com/services/XXXXXXXX/XXXXXXXXX/XXXXXXXXXXX3",
    }
}

msteams_conf = {
    "enabled": True,
    "default_url": "https://outlook.office.com/webhook/xxxxxxxxxxxx/IncomingWebhook/xxxxxxxxxxx/xxxxxxxxxxx",
    "url": {
        "debug": "https://outlook.office.com/webhook/xxxxxxxxxxxx/IncomingWebhook/xxxxxxxxxxx/xxxxxxxxxxx",
        "info": "https://outlook.office.com/webhook/xxxxxxxxxxxx/IncomingWebhook/xxxxxxxxxxx/xxxxxxxxxxx",
        "warning": "https://outlook.office.com/webhook/xxxxxxxxxxxx/IncomingWebhook/xxxxxxxxxxx/xxxxxxxxxxx",
        "critical": "https://outlook.office.com/webhook/xxxxxxxxxxxx/IncomingWebhook/xxxxxxxxxxx/xxxxxxxxxxx"
    }
}

event_channels = {
    "AP_CLAIMED": "warning",
    "AP_UNCLAIMED": "warning",
    "AP_ASSIGNED": "info",
    "AP_UNASSIGNED": "info",
    "AP_CONFIG_CHANGED_BY_RRM": "debug",
    "AP_CONFIG_CHANGED_BY_USER": "info",
    "AP_CONFIG_FAILED": "critical",
    "AP_CONFIGURED": "debug",
    "AP_RECONFIGURED": "debug",
    "1026": "debug",
    "AP_RRM_ACTION": "debug",
    "AP_BEACON_STUCK": "critical",
    "AP_RESTART_BY_USER": "info",
    "AP_RESTARTED": "info",
    "AP_CONNECTED": "info",
    "AP_DISCONNECTED": "info",
    "AP_DISCONNECTED_LONG": "warning",
    "AP_UPGRADED": "info",
    "AP_UPGRADE_BY_SCHEDULE": "debug",
    "AP_UPGRADE_BY_USER": "debug",
    "AP_UPGRADE_FAILED": "critical",
    "AP_RADAR_DETECTED": "info",
    "AP_CERT_REGENERATED": "debug",
    "AP_GET_SUPPORT_FILES": "debug",
    "AP_RADIUS_ACCOUNTING_SERVER_CHANGE": "info",
    "AP_RADIUS_AUTHENTICATION_SERVER_CHANGE": "info",
    "AP_RADSEC_FAILURE": "critical",
    "AP_RADSEC_SERVER_CHANGE": "info",
    "AP_RADSEC_RECOVERY": "info",

    "GW_CLAIMED": "warning",
    "GW_UNCLAIMED": "warning",
    "GW_ASSIGNED": "info",
    "GW_UNASSIGNED": "info",
    "GW_ZTP_FINISHED": "info",
    "GW_CONFIG_CHANGED_BY_USER": "info",
    "GW_CONFIG_GENERATED": "debug",
    "GW_RECONFIGURED": "debug",
    "GW_CONFIGURED": "debug",
    "GW_CONFIG_LOCK_FAILED": "warning",
    "GW_CONFIG_FAILED": "warning",
    "GW_PORT_UP": "info",
    "GW_PORT_DOWN": "info",
    "GW_CONNECTED": "info",
    "GW_DISCONNECTED": "info",
    "GW_DISCONNECTED_LONG": "warning",
    "GW_RESTARTED": "info",
    "GW_RESTARTED_BY_USER": "info",
    "GW_OSPF_NEIGHBOR_UP": "debug",
    "GW_OSPF_NEIGHBOR_DOWN": "debug",
    "GW_BGP_NEIGHBOR_STATE_CHANGED": "debug",
    "GW_VPN_PATH_DOWN": "debug",
    "GW_VPN_PATH_UP": "debug",
    "GW_VPN_PEER_UP": "debug",
    "GW_VPN_PEER_DOWN": "debug",
    "GW_CERT_REGENERATED": "debug",
    "GW_ALARM": "warning",
    "GW_UPGRADE_BY_USER": "debug",
    "GW_UPGRADED": "debug",
    "GW_UPGRADE_PENDING": "debug",
    "GW_UPGRADE_FAILED": "warning",
    "GW_CONDUCTOR_CONNECTED": "info",
    "GW_ARP_RESOLVED": "info",
    "GW_ARP_UNRESOLVED": "warning",
    "GW_DHCP_RESOLVED": "debug",
    "GW_DHCP_UNRESOLVED": "warning",
    "GW_HA_CONTROL_LINK_UP": "info",
    "GW_HA_CONTROL_LINK_DOWN": "warning",
    "GW_HA_HEALTH_WEIGHT_LOW": "warning",
    "GW_HA_HEALTH_WEIGHT_RECOVERY": "info",
    "GW_CONDUCTOR_DISCONNECTED": "warning",
    "GW_SYSTEM_SERVICE_RESTART": "warning",
    "GW_REJECTED": "critical",
    "GW_RG_STATE_CHANGED": "info",
    "GW_PORT_RG_STATE_CHANGED": "info",
    "GW_PORT_RG_ST_CHANGED": "info",
    "GW_RESTART_BY_USER": "debug",
    "GW_ALARM_POE_CONTROLLER_UPGRADE_AVAILABLE": "warning",
    "GW_UPGRADE_BY_MIST": "info",

    "SW_CLAIMED": "warning",
    "SW_UNCLAIMED": "warning",
    "SW_ASSIGNED": "info",
    "SW_UNASSIGNED": "info",
    "SW_ZTP_FINISHED": "info",
    "SW_CONFIG_CHANGED_BY_USER": "info",
    "SW_RECONFIGURED": "debug",
    "SW_CONFIG_GENERATED": "debug",
    "SW_CONFIGURED": "debug",
    "SW_CONFIG_LOCK_FAILED": "warning",
    "SW_CONFIG_FAILED": "warning",
    "SW_PORT_UP": "debug",
    "SW_PORT_DOWN": "debug",
    "SW_CONNECTED": "info",
    "SW_DISCONNECTED": "info",
    "SW_RESTARTED": "info",
    "SW_RESTART_BY_USER": "info",
    "SW_OSPF_NEIGHBOR_UP": "debug",
    "SW_OSPF_NEIGHBOR_DOWN": "debug",
    "SW_BGP_NEIGHBOR_STATE_CHANGED": "debug",
    'SW_ALARM': "warning",
    'SW_ALARM_CHASSIS_PARTITION': "warning",
    'SW_ALARM_CHASSIS_POE': "warning",
    'SW_ALARM_CHASSIS_PSU': "warning",
    "SW_UPGRADE_BY_USER": "debug",
    "SW_UPGRADED": "debug",
    "SW_UPGRADE_PENDING": "debug",
    "SW_UPGRADE_FAILED": "critical",
    'SW_SYSTEM_SERVICE_RESTART': "warning",
    'SW_REJECTED': "critical",
    "SW_DYNAMIC_PORT_ASSIGNED": "info",
    'SW_PORT_BPDU_BLOCKED': "warnning",
    'SW_PORT_STORM_CONTROL': "warnning",
    'SW_HANDSHAKE_ERROR': "warning",
    'SW_STP_TOPO_CHANGED': "info",
    'SW_VC_BACKUP_ELECTED': "warning",
    'SW_VC_MASTER_CHANGED': "warning",
    'SW_VC_MEMBER_ADDED': "info",
    'SW_VC_MEMBER_DELETED': "warning",
    'SW_MASTER_ON_RECOVERY': "warning",
    'SW_MEMBER_ON_RECOVERY': "warning",
    'SW_RECOVERY_SNAPSHOT_REQUESTED': "info",
    'SW_RECOVERY_SNAPSHOT_SUCCEEDED': "info",
    'SW_RECOVERY_SNAPSHOT_FAILED': "warning",
    'SW_RECOVERY_SNAPSHOT_NOTNEEDED': "warning",
    'SW_RECOVERY_SNAPSHOT_UNSUPPORTED': "info",
    "SW_DOT1XD_USER_AUTHENTICATED": "debug",
    "SW_RADIUS_SERVER_UNREACHABLE": "warning",
    "SW_ALARM_POE_CONTROLLER_UPGRADE_AVAILABLE": "warning",

    "ME_CLAIMED": "warning",
    "ME_UNCLAIMED": "warning",
    "ME_ASSIGNED": "info",
    "ME_UNASSIGNED": "info",
}

updown_channels = {
    "AP_CONNECTED": "info",
    "AP_DISCONNECTED": "info",
    "AP_RESTARTED": "info",
    "GW_CONNECTED": "info",
    "GW_DISCONNECTED": "info",
    "GW_RESTARTED": "info",
    "SW_CONNECTED": "info",
    "SW_DISCONNECTED": "info",
    "SW_RESTARTED": "info"
}

alarm_channels = {
    # infrastructure
    "device_down": "warning",
    "device_restarted": "info",
    "switch_down": "warning",
    "switch_restarted": "info",
    "gateway_down": "warning",
    "device_reconnected": "info",
    "switch_reconnected": "info",
    "gateway_reconnected": "info",
    "vpn_peer_down": "warning",
    "vc_master_changed": "critical",
    "vc_backup_failed": "critical",
    "vc_member_added": "info",
    "vc_member_deleted": "critical",
    "sw_alarm_chassis_poe": "warning",
    "sw_alarm_chassis_pem": "warning",
    "sw_alarm_chassis_psu": "warning",
    "sw_alarm_chassis_partition": "warning",
    "sw_dhcp_pool_exhausted": "warning",
    "gw_dhcp_pool_exhausted": "warning",
    "sw_bgp_neighbor_state_changed": "info",
    "sw_bad_optics": "warning",
    "sw_bpdu_error": "warning",
    "loop_detected_by_ap": "warning",
    "infra_dhcp_failure": "critical",
    "infra_dhcp_success": "info",
    "infra_dns_failure": "critical",
    "infra_dns_success": "info",
    "infra_arp_failure": "critical",
    "infra_arp_success": "info",

    # security
    "secpolicy_violation": "warning",
    "bssid_spoofing": "info",
    "honeypot_ssid": "info",
    "adhoc_network": "warning",
    "rogue_ap": "critical",
    "rogue_client": "critical",
    "watched_station": "warning",
    "eap_handshake_flood": "info",
    "air_magnet_scan": "info",
    "excessive_eapol_start": "warning",
    "eapol_logoff_attack": "warning",
    "eap_dictionary_attack": "warning",
    "disassociation_flood": "warning",
    "beacon_flood": "warning",
    "essid_jack": "warning",
    "krack_attack": "warning",
    "vendor_ie_missing": "warning",
    "tkip_icv_attack": "warning",
    "repeated_auth_failures": "info",
    "eap_failure_injection": "warning",
    "eap_spoofed_success": "warning",
    "out_of_sequence": "warning",
    "zero_ssid_association": "warning",
    "monkey_jack": "warning",
    "excessive_client": "warning",
    "ssid_injection": "warning",
    # marvis
    "missing_vlan": "critical",
    "bad_cable": "critical",
    "port_flap": "warning",
    "gw_bad_cable": "critical",
    "authentication_failure": "critical",
    "dhcp_failure": "critical",
    "arp_failure": "critical",
    "dns_failure": "critical",
    "negotiation_mismatch": "critical",
    "gw_negotiation_mismatch": "critical",
    "ap_offline": "warning",
    "non_compliant": "warning",
    "ap_bad_cable": "critical",
    "health_check_failed": "warning",
    "bad_wan_uplink": "critical",
    "switch_stp_loop": "critical",
    "insufficient_coverage": "critical",
    "insufficient_capacity": "critical"
}

audit_channels = {
    "approved_admins": "debug",
    "other_admins": "critical"
}

mxedge_events = {
    "ME_CONFIG_CHANGED_BY_USER": "info",
    "ME_SERVICE_STOPPED": "debug",
    "ME_SERVICE_STARTED": "debug",
    "ME_SERVICE_RESTARTED": "debug",
    "ME_SERVICE_FAILED": "critical",
    "TT_TUNNELS_LOST": "warning",
    "ME_RESTARTED": "info",
    "ME_RESOURCE_USAGE": "warning",
    "ME_CONFIGURED": "debug",
    "ME_CONNECTED": "info",
    "ME_DISCONNECTED": "warning",
    "ME_RESTART_BY_USER": "info",
    "ME_PACKAGE_INSTALLED": "info",
    "ME_PACKAGE_UNINSTALLED": "debug",
    "ME_PACKAGE_INSTALL_FAILED": "critical",
    "ME_PACKAGE_UNINSTALL_FAILED": "warning",
    "ME_PACKAGE_UPDATED": "info",
    "ME_PACKAGE_UPDATE_BY_USER": "info",
    "ME_PACKAGE_UPDATE_FAILED": "warning",
    "ME_SERVICE_CRASHED": "critical",
    "TT_PORTS_BOUNCE_BY_USER": "info",
    "TT_PORTS_BOUNCED": "info",
    "TT_PORTS_BOUNCE_FAILED": "warning",
    "TT_AP_DISCONNECT_BY_USER": "info",
    "TT_AP_DISCONNECTED": "info",
    "TT_AP_DISCONNECT_FAILED": "warning",
    "ME_FAN_PLUGGED": "info",
    "ME_FAN_UNPLUGGED": "critical",
    "ME_PSU_PLUGGED": "info",
    "ME_PSU_UNPLUGGED": "critical",
    "ME_POWERINPUT_CONNECTED": "info",
    "ME_POWERINPUT_DISCONNECTED": "critical",
    "TT_PORT_BLOCKED": "warning",
    "TT_PORT_RECOVERY": "info",
    "TT_PORT_LINK_DOWN": "warning",
    "TT_PORT_LINK_RECOVERY": "info",
    "TT_PORT_DROPPED_FROM_LACP": "warning",
    "TT_PORT_JOINED_LACP": "info",
}


EOF
     echo -e "${ERRORC}IMPORTANT${NC}: If you didn't customized your configuration file yet, please do it now,"
    echo "before stating the app containers!"
    echo ""
    response="xx"
    while ! echo "x$response" | grep "xy" > /dev/null
    do
      echo "Do you want to want start the App now [y/N]? " 
      read response
      case "x$response" in
        "xy") break;;
        "xn") exit 0;;
      esac
    done
  fi
}

################################################################################
############################    SCRIPT CONF
################################################################################

function script_conf
{
  # FOLDER PARAMETERS
  echo "We will need a persistant folder to store application configuration, data and certificates."
  echo "Where do you want to store these data? [$PERSISTANT_FOLDER]"
  echo ""
  response=""
  while ! echo $response | grep -i "y" > /dev/null
  do
    read -p "PERSISTANT FOLDER: " PERSISTANT_FOLDER
    if ! echo $PERSISTANT_FOLDER | grep ^"/" > /dev/null
    then
      echo -e "${WARNINGC}WARNING${NC}: Incorrect input"
    else
      read -p "Is \"$PERSISTANT_FOLDER\" correct (y/n)? " response
    fi
  done
  while [ ! -d "$PERSISTANT_FOLDER" ]
  do
    echo "$PERSISTANT_FOLDER does not exist."
    create=""
    while ! echo $create | grep -i "[ny]" > /dev/null
    do
      read -p "Do you want to create it (y/n)? " create
      case $create in
        "y"|"Y") mkdir -p "$PERSISTANT_FOLDER/$APP_NAME";;
        *) exit 0;;
      esac
    done
  done
  # VHOST PARAMETER
  echo ""
  echo ""

  # SAVING PARAMETERS
  if [ -f $SCRIPT_CONF ]
  then
    mv $SCRIPT_CONF $SCRIPT_CONF.bak
  fi
  touch $SCRIPT_CONF
  while read line
  do
    if echo "$line" | grep "VHOST" > /dev/null
    then
      echo "$line" >> $SCRIPT_CONF
    fi
  done < $SCRIPT_CONF.bak
  echo "" >> $SCRIPT_CONF
  echo "PERSISTANT_FOLDER=$PERSISTANT_FOLDER" >> $SCRIPT_CONF
  echo "" >> $SCRIPT_CONF
}

function update_vhost
{
  echo "To use the NGINX reverse proxy, we will need a dedicated DNS entry for the application."
  echo "Web browsers will access the application interface from this FQDN."
  response=""
  while ! echo "x$response" | grep -i "xy" > /dev/null
  do
    read -p "Application DNS name: " APP_VHOST
    read -p "Are you sure (y/n)? " response
    echo ""
  done
  echo "$APP_NAME-APP_VHOST=$APP_VHOST" >> $SCRIPT_CONF
  echo "" >> $SCRIPT_CONF
}

function init_script_conf
{
  if [ ! -f "$SCRIPT_CONF" ]
  then
    echo "-----=============-----"
    echo "--=== SCRIPT INIT ===--"
    echo ""
    echo "Before starting, here are some questions..."
    echo ""
    script_conf
    response=""
    while ! echo $response | grep -i "[y]" > /dev/null
    do
      echo ""
      echo "Current parameters:"
      echo ""
      cat $SCRIPT_CONF
      read -p "Is the configuration correct (y/n)? " response
      case $response in
        "n"|"N") script_conf;;
      esac
    done
  else
    while read line
    do
      if echo $line | grep "PERSISTANT_FOLDER" > /dev/null
      then
        PERSISTANT_FOLDER=`echo "$line" | cut -d"=" -f2`
      fi
      if echo $line | grep "$APP_NAME-APP_VHOST" > /dev/null
      then
        APP_VHOST=`echo "$line" | cut -d"=" -f2`
      fi
    done < $SCRIPT_CONF
  fi
  if echo "$PERSISTANT_FOLDER" | grep -i [a-z] > /dev/null
  then
    MONGO_FOLDER="$PERSISTANT_FOLDER/$DB_FOLDER"
    NGINX_CERTS_FOLDER="$PERSISTANT_FOLDER/$NGINX_CERTS_FOLDER"
    DOCKER_COMPOSE_FOLDER="$PERSISTANT_FOLDER/container-enable"
    echo -e "${INFOC}INFO${NC}: Script configuration loaded succesfully."
  else
    echo -e "${ERRORC}ERROR${NC}: not able to load Script configuration. Exiting..."
    exit 254
  fi
  if [ ! "$APP_VHOST" ]
  then
    update_vhost    
  fi
}

function read_script_conf
{
  if [ ! -f $SCRIPT_CONF ]
  then
    echo -e "${WARNINGC}WARNING${NC}: Script configuration file does not exists..."
    script_conf
  fi
  echo ""
  echo "Current parameters:"
  echo ""
  cat $SCRIPT_CONF
}

function menu_script
{
  response=""
  while ! echo $response | grep -i "[b]" > /dev/null
  do
    echo ""
    echo "1) Change Script parameters"
    echo "2) View Script parameters"
    echo "b) Back"
    echo "Please make a choice"
    read response
    case "x$response" in
      "x1") script_conf;;
      "x2") read_script_conf;;
      "xb") menu_main;;
    esac
  done
}


################################################################################
############################    FOLDERS
################################################################################

function check_folder # $name $FOLDER_NAME
{
  if [ ! -d $2 ]
  then
    echo -e "${INFOC}INFO${NC}: $1 folder $2 doesn't exist. Creating it..."
    mkdir -p $2
    if [ $? -eq 0 ]
    then
      echo -e "${INFOC}INFO${NC}: $1 folder $2 created."
    else
      echo ""
      echo -e "${ERRORC}ERROR${NC}: Unable to create $1 folder $2."
    fi
  else
    echo -e "${INFOC}INFO${NC}: $1 folder already exists."
  fi
}

################################################################################
############################    CERTIFICATES
################################################################################

function check_certificates
{
    if [ `ls $NGINX_CERTS_FOLDER | grep $APP_VHOST.key | wc -l` -eq 0 ] || [ `ls $NGINX_CERTS_FOLDER | grep $APP_VHOST.crt | wc -l` -eq 0 ]
    then
        echo -e "${INFOC}INFO${NC}: Certificates for $APP_VHOST doesn't exist."
        echo "     Creating a self-signed certificate..."
        openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout $NGINX_CERTS_FOLDER/$APP_VHOST.key -out $NGINX_CERTS_FOLDER/$APP_VHOST.crt
        echo -e "${INFOC}INFO${NC}: Certificate for $APP_VHOST created."
    else
        echo -e "${INFOC}INFO${NC}: Certificate for $APP_VHOST already exists."
    fi
}

function new_certificate
{
    if [ -f "$NGINX_CERTS_FOLDER/$APP_VHOST.crt" ]
    then
      echo -e "${INFOC}INFO${NC}: removing $NGINX_CERTS_FOLDER/$APP_VHOST.crt"
      rm $NGINX_CERTS_FOLDER/$APP_VHOST.crt
    fi
    if [ -f "$NGINX_CERTS_FOLDER/$APP_VHOST.key" ]
    then
      echo -e "${INFOC}INFO${NC}: removing $NGINX_CERTS_FOLDER/$APP_VHOST.key"
      rm $NGINX_CERTS_FOLDER/$APP_VHOST.key
    fi
    openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout $NGINX_CERTS_FOLDER/$APP_VHOST.key -out $NGINX_CERTS_FOLDER/$APP_VHOST.crt
    echo -e "${INFOC}INFO${NC}: Certificate for $APP_VHOST created."
  
}

function new_csr
{
  openssl req -out $NGINX_CERTS_FOLDER/$APP_VHOST.csr -new -newkey rsa:2048 -nodes -keyout $NGINX_CERTS_FOLDER/$APP_VHOST.key
  echo -e "${INFOC}INFO${NC}: new CSR generated. The CSR $APP_VHOST.csr can be found in the folder $NGINX_CERTS_FOLDER"
  echo -e "${WARNINGC}WARNING${NC}: To be able to use the application, you will have to sign the CSR with"
  echo "         your Certificate Authority."
  echo "         The signed certificate has to be place into the folder"
  echo "         $NGINX_CERTS_FOLDER with the name $APP_VHOST.crt"
}

function help_certificate
{
  echo -e "${INFOC}INFO${NC}: You can replace the self-signed certicate with your own certicate."
  echo "      To do so, you will have to generate a signed certificate on your own,"
  echo "      and to place the certificate and its private key into the folder"
  echo "      $NGINX_CERTS_FOLDER"
  echo "      The certificate has to be a X509 certificate in PEM format."
  echo "      At the end, you should have:"
  echo "      $NGINX_CERTS_FOLDER/$APP_VHOST.crt"
  echo "      $NGINX_CERTS_FOLDER/$APP_VHOST.key"
}

function read_certificate
{
  openssl x509 -in $NGINX_CERTS_FOLDER/$APP_VHOST.crt -noout -text
}

function menu_certificates
{
  response=""
  while ! echo "x$response" | grep -i "xb" > /dev/null
  do
    echo ""
    echo "1) Generate new self-signed certificate"
    echo "2) Generate CSR"
    echo "3) Help to use custom certificate"
    echo "4) View current Certificate"
    echo "b) Back"
    echo "Please make a choice"
    read response
    case $response in
      "x1") new_certificate;;
      "x2") new_csr;;
      "x3") help_certificate;;
      "x4") read_certificate;;
      "xb") menu_main;;
    esac
  done
}



################################################################################
############################    FILES VALIDATORS
################################################################################
function generate_docker_compose_file 
{
  case $1 in
    "nginx") generate_docker_compose_ngninx;;
    "mongodb") generate_docker_compose_mongodb;;
    $APP_NAME) generate_docker_compose_app;;
  esac 
}

function check_docker_compose_file
{
  if [ ! -f "$PERSISTANT_FOLDER/$APP_NAME/docker-compose.$1.yaml" ]
  then
    echo -e "${ERRORC}ERROR${NC}: Unable to find the docker-compose file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$1.yaml"
    generate_docker_compose_file $1
  else
    echo -e "${INFOC}INFO${NC}: docker-compose file found in $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$1.yaml"
  fi
}

function check_docker_compose_files
{
  if [ "$NGINX_IMG" ]
  then
    check_docker_compose_file "nginx"
  fi
  if [ "$DB_IMG" ]
  then
    check_docker_compose_file "mongodb"
  fi
  check_docker_compose_file "$APP_NAME"
  
}

function check_configuration_file
{
  if [ ! -f $PERSISTANT_FOLDER/$APP_NAME/config.py ]
  then
    echo -e "${ERRORC}ERROR${NC}: Unable to find the configuration file for $APP_NAME."
    generate_conf_file
  else
    echo -e "${INFOC}INFO${NC}: configuration file found in $PERSISTANT_FOLDER/$APP_NAME/config.py"
  fi
}


################################################################################
############################    START
################################################################################

function result_banner
{
  echo ""
  echo ""
  echo "============================================================================"
  echo "============================================================================"
  echo "                  The system is now up and running!"
  echo ""
  echo -e "${INFOC}INFO${NC}: NGINX SSL/TLS certifcates are in $NGINX_CERTS_FOLDER"
  echo ""
  echo -e "${INFOC}INFO${NC}: MongoDB files are in $MONGO_FOLDER"
  echo ""
  echo ""
  echo -e "${INFOC}INFO${NC}: $APP_NAME interface should now be avaible soon"
  echo "      https://$APP_VHOST"
  echo ""
  echo "============================================================================"
  echo "============================================================================"
}

function get_active_compose_files
{
  compose_files=""
  for i in `ls $DOCKER_COMPOSE_FOLDER`
  do 
    if echo "$i" | grep -q ".yaml"$
    then 
    R_PATH=`realpath $DOCKER_COMPOSE_FOLDER/$i`
      compose_files="$compose_files -f $R_PATH"
    fi
  done
  echo "$compose_files"
}

function enable_docker_compose
{
  if [ ! -f $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml ]
  then
    ln -s $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml
  fi
  if [ "$NGINX_IMG" ] && [ ! -f $DOCKER_COMPOSE_FOLDER/docker-compose.nginx.yaml ]
  then
    ln -s $PERSISTANT_FOLDER/$APP_NAME/docker-compose.nginx.yaml $DOCKER_COMPOSE_FOLDER/docker-compose.nginx.yaml
  fi
  if [ "$DB_IMG" ] && [ ! -f $DOCKER_COMPOSE_FOLDER/docker-compose.mongodb.yaml ]
  then
    ln -s $PERSISTANT_FOLDER/$APP_NAME/docker-compose.mongodb.yaml $DOCKER_COMPOSE_FOLDER/docker-compose.mongodb.yaml
  fi
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.nginx.yaml up -d
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.mongodb.yaml up -d
}

function disable_docker_compose
{
  if [ -f $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml ]
  then
    rm $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml
  fi
}

function start_container # CONT NAME
{
  enable_docker_compose
  compose_files="$(get_active_compose_files)"
  docker-compose $compose_files start $1
  retvalAPP=$?
  if [ $retvalAPP -eq 0 ] 
  then
    echo ""
    echo -e "${INFOC}INFO${NC}: Container $1 is now started..."
  else
    echo ""
    echo -e "${WARNINGC}WARNING${NC}: Unable to start the container $1..."
  fi
  echo ""
}

function start_containers
{
  enable_docker_compose
  compose_files="$(get_active_compose_files)"
  docker-compose $compose_files start
  retvalAPP=$?
  if [ $retvalAPP -eq 0 ] 
  then
    result_banner
  else
    echo ""
    echo -e "${WARNINGC}WARNING${NC}: Some containers are not started. The Application may not"
    echo "         be accesssible."
    echo "         Please fix the errors and retry."
    echo ""
    echo "         You can try to deploy the Application to (re)create the required containers."    
  fi
  echo ""
}


function stop_container # CONT NAME
{
  if [ -f $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml ]
  then
    $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.yaml stop $1
    disable_docker_compose
    retvalAPP=$?
  else
    retvalAPP=0
  fi
  if [ $retvalAPP -eq 0 ] 
  then
    echo ""
    echo -e "${INFOC}INFO${NC}: Container $1 is now stopped..."
  else
    echo ""
    echo -e "${WARNINGC}WARNING${NC}: Unable to stop the container $1..."
  fi
  echo ""
}

function stop_containers
{
  if [ -f $DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml ]
  then
    $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml stop
    disable_docker_compose
    retvalAPP=$?
  else
    retvalAPP=0
  fi  
  if [ $retvalAPP -eq 0 ] 
  then
    echo ""
    echo -e "${INFOC}INFO${NC}: All the containers for this app are now stopped..."
    compose_files="$(get_active_compose_files)"
    if [ -n "$compose_files" ]
    then
      docker-compose $compose_files start
    fi
  else
    echo ""
    echo -e "${WARNINGC}WARNING${NC}: Unable to stop some of the containers..."
  fi
  echo ""
}
################################################################################
############################    DEPLOY
################################################################################
function auto_deploy
{  
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml up --no-start 
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml start 
  start_containers
}

function deploy
{
  echo "-----=============-----"
  echo "--=== DEPLOY INIT ===--"
  echo ""
  echo ""
  echo "This script is using docker-compose to automatically"
  echo "  - Download Docker Images (NGINX, MONGODB, APP)"
  echo "  - Create Docker Containers based on the configuration you gave"
  echo "  - Start Docker Containers"
  echo ""
  response=""
  while ! echo "$response" | grep -i "[yn]" > /dev/null
  do

    read -p "Do you want to continue (y/n)? " response
    case $response in
      "y"|"Y") auto_deploy;;
    esac
  done
}

################################################################################
############################    UPDATE
################################################################################
function update_app
{
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml stop  
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml rm --force
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml pull
  $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml up --no-start
  if [ -f "$DOCKER_COMPOSE_FOLDER/docker-compose.$APP_NAME.yaml" ]
  then
    $DOCKER_COMP --file $PERSISTANT_FOLDER/$APP_NAME/docker-compose.$APP_NAME.yaml start
  fi
}


################################################################################
############################    INIT
################################################################################
function check_docker
{
  DOCKER=`which docker`
  if ! echo "$DOCKER" | grep -i "docker" > /dev/null
  then
    echo -e "${ERRORC}ERROR${NC}: Unable to find docker path."
    echo "       Plese install docker first: https://www.docker.com/products/overview"
    echo "Exiting..."
    exit 255
  else
    echo -e "${INFOC}INFO${NC}: docker found at $DOCKER"
  fi
}

function check_docker_compose
{
  DOCKER_COMP=`which docker-compose`
  if ! echo "$DOCKER_COMP" | grep -i "docker-compose" > /dev/null
  then
    echo -e "${ERRORC}ERROR${NC}: Unable to find docker-compose path."
    echo "       Plese install docker docker-compose: https://www.docker.com/products/overview"
    echo "Exiting..."
    exit 255
  else
    echo -e "${INFOC}INFO${NC}: docker-compose found at $DOCKER_COMP"
  fi
}

function init_script
{
  banner "$APP_NAME Management Script"

  check_docker
  check_docker_compose

  init_script_conf

  check_folder "container-enable" $DOCKER_COMPOSE_FOLDER
  check_folder "Database" $MONGO_FOLDER
  check_folder "Certificates" $NGINX_CERTS_FOLDER
  check_folder "App" "$PERSISTANT_FOLDER/$APP_NAME"
  

  check_certificates

  check_configuration_file
  check_docker_compose_files

  echo -e "${INFOC}INFO${NC}: Script init done."
  echo "||============================================================================="
  echo ""
 
}

function menu_main
{
  response="0"
  while ! echo "x$response" | grep -i "xx" > /dev/null
  do
    echo ""
    echo "1) Deploy and Start Application"
    echo "2) Start Application Containers"
    echo "3) Stop Application Containers"
    echo "4) Update Application"
    echo "5) HTTPS certificates"
    echo "6) Script parameters"
    echo "x) Exit"
    echo "Please make a choice"
    read response
    case "x$response" in
      "x1") deploy;;
      "x2") start_containers;;
      "x3") stop_containers;;
      "x4") update_app;;
      "x5") menu_certificates;;
      "x6") menu_script;;      
      "xx") exit 0;;
    esac
  done
}


################################################################################
############################    USAGE
################################################################################
usage ()
{
cat <<EOF

NAME
        $SCRIPT_NAME - Installation, Configuration and Control script
                    for $APP_NAME app

SYNOPSIS
        $SCRIPT_NAME [WORD]

DESCRIPTION
        This script will run the action to install, configure and control the
        needed docker containers for Get-a-Key web app.

options are
        start         Validates the configuration and starts all the containers
                      If needed, this will download and install all the needed
                      containers.
        stop          Stops all the containers.
        restart       Same as "stop all" and "start all"
        list          List the containers used by this app.

        help          this help
EOF
}




################################################################################
############################    ENTRY POINT
################################################################################


if [ $# -eq 0 ]
then
  init_script
  menu_main
elif [ $# -eq 1 ]
then
  case $1 in
    "start") init_script; start_containers;;
    "stop") init_script; stop_containers;;
    "restart") init_script; stop_containers; start_containers;;
    "list") init_script; check_containers;;
    *) usage; exit 1;;
  esac
else
  usage
  exit 1
fi