from pytest_homeassistant_custom_component.common import load_json_object_fixture

INFO = [load_json_object_fixture("info.json")]
MEM = [load_json_object_fixture("memory.json")]
LEDS = [load_json_object_fixture("leds.json")]
DEVICES = [load_json_object_fixture("devices.json")]
WAN_IP_STATS = [load_json_object_fixture("wan_ip_stats.json")]
PARENTALCONTROL = [load_json_object_fixture("parentalcontrol.json")]
WPS = [load_json_object_fixture("wps.json")]
WIFI = [load_json_object_fixture("wifi.json")]
WAN_IP = [load_json_object_fixture("wan_ip.json")]
SPEEDTEST_INFOS = [load_json_object_fixture("speedtest.json")]

MOCK_USER_INPUT = {
    "host": "192.168.1.1",
    "password": "mock_password",
    "use_tls": False,
    "verify_ssl": False,
}
