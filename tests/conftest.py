from pyapp.conf import settings

# Ensure settings are configured
settings.configure(
    ["pyapp_ext.messaging.default_settings", "pyapp_ext.aiobotocore.default_settings"]
)
