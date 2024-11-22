"""Constants for the Bouygues Bbox integration."""

DOMAIN = "bbox"
BBOX_NAME = "Bbox"
MANUFACTURER = "Bouygues"
DEFAULT_TITLE = f"{MANUFACTURER} {BBOX_NAME}"
CONF_PASSWORD = "password"
CONF_HOST = "host"
CONF_USE_TLS = "use_tls"
CONF_REFRESH_RATE = "refresh_rate"

CONF_DEFAULTS = {
    CONF_HOST: "mabbox.bytel.fr",
    CONF_USE_TLS: True,
    CONF_REFRESH_RATE: 60,
}
TO_REDACT = {
    "username",
    "password",
    "encryption_password",
    "encryption_salt",
    "host",
    "api_key",
    "serial",
    "system_serial",
    "ip4_addr",
    "ip6_addr",
    "account",
    "key",
}
