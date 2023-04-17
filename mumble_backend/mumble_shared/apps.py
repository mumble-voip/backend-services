from django.apps import AppConfig


class MumbleSharedConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mumble_shared"

    AUTHORIZED_HASHES = {
        # 'testpassword'
        "ebe5a79f942bab98b3c122ceb72a9c23fb21991848cddb9ad4ce8a209c8269c25eb5f5146427afc23ef588de61798b38451282339e2c637c6dec51d635ab50c4"
    }
