SCRIPT: monitorizare.py 
import time
import xmltodict
from ncclient import manager
from influxdb import InfluxDBClient
import warnings
warnings.filterwarnings("ignore")
DEVICES = [
    {"name": "R1", "ip": "10.0.1.1", "user": "cisco", "password": "cisco"},
    {"name": "R2", "ip": "10.0.1.2", "user": "cisco", "password": "cisco"},
    {"name": "R3", "ip": "10.0.2.2", "user": "cisco", "password": "cisco"}
]
INFLUX_HOST = "localhost"
INFLUX_PORT = 8086
DB_NAME     = "network_monitoring"
INTERVAL    = 10  # seconds between collection cycles
NETCONF_FILTER = """
<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name/>
      <statistics>
        <in-octets/>
        <out-octets/>
      </statistics>
    </interface>
  </interfaces-state>
</filter>
"""
client = InfluxDBClient(host=INFLUX_HOST, port=INFLUX_PORT)
client.create_database(DB_NAME)
client.switch_database(DB_NAME)
# Dictionary storing the previous collection cycle values per device/interface
previous_values = {}
def get_netconf_interfaces(ip, user, password):
    with manager.connect(
        host=ip,
        port=830,
        username=user,
        password=password,
        hostkey_verify=False,
        look_for_keys=False,
        allow_agent=False,
        timeout=10
    ) as m:
        response        = m.get(NETCONF_FILTER)
        parsed          = xmltodict.parse(response.xml)
        rpc_reply       = parsed.get("rpc-reply", {})
        data            = rpc_reply.get("data", {})
        interfaces_root = data.get("interfaces-state", {})
        interfaces      = interfaces_root.get("interface", [])
        if isinstance(interfaces, dict):
            interfaces = [interfaces]
        return interfaces
def collect_data():
    while True:
        for dev in DEVICES:
            try:
                interfaces = get_netconf_interfaces(
                    dev["ip"], dev["user"], dev["password"]
                )
                for iface in interfaces:
                    if_name = iface.get("name", "unknown")
                    if not str(if_name).startswith("GigabitEthernet"):
                        continue
                    stats      = iface.get("statistics", {})
                    traffic_in  = int(stats.get("in-octets",  0) or 0)
                    traffic_out = int(stats.get("out-octets", 0) or 0)
                    # Unique key per router + interface
                    key  = f"{dev['name']}_{if_name}"
                    prev = previous_values.get(key)
                    # First collection cycle — establish baseline reference,
                    # do not write to InfluxDB
                    if prev is None:
                        previous_values[key] = {
                            "in":  traffic_in,
                            "out": traffic_out
                        }
                        print(f"[{dev['name']}] {if_name} — baseline established")
                        continue
                    # Delta calculation
                    delta_in  = traffic_in  - prev["in"]
                    delta_out = traffic_out - prev["out"]
                    # Ignore negative values — counter reset on router restart
                    if delta_in  < 0: delta_in  = 0
                    if delta_out < 0: delta_out = 0
                    # Calculate rates in bps
                    rate_in_bps  = (delta_in  * 8) / INTERVAL
                    rate_out_bps = (delta_out * 8) / INTERVAL
                    # Update previous values
                    previous_values[key] = {
                        "in":  traffic_in,
                        "out": traffic_out
                    }
                    # Write real-time rates to InfluxDB
                    data = [
                        {
                            "measurement": "network_traffic",
                            "tags": {
                                "device":    dev["name"],
                                "interface": str(if_name)
                            },
                            "fields": {
                                "download": rate_in_bps,
                                "upload":   rate_out_bps
                            }
                        }
                    ]
                    client.write_points(data)
                    # Console output
                    print(
                        f"[{dev['name']}] {if_name} | "
                        f"IN: {rate_in_bps/1000:.2f} kb/s | "
                        f"OUT: {rate_out_bps/1000:.2f} kb/s"
                    )
            except Exception as e:
                print(f"[ERROR] {dev['name']} ({dev['ip']}): {e}")
        time.sleep(INTERVAL)
if __name__ == "__main__":
    print("NETCONF monitoring system started...")
    collect_data()
