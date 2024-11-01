from chaoslib.exceptions import InvalidExperiment
import logging
from typing import Dict

from chaoslib.types import Configuration, Secrets

try:
    import hvac

    HAS_HVAC = True
except ImportError:
    HAS_HVAC = False

logger = logging.getLogger("chaostoolkit")


def load_secrets_from_vault(
        secrets_info: Dict[str, Dict[str, str]],  # noqa: C901
        configuration: Configuration = None,
) -> Secrets:
    """
    Load secrets from Vault KV secrets store

    In your experiment:

    ```
    {
        "k8s": {
            "mykey": {
                "type": "vault",
                "path": "foo/bar"
            }
        }
    }
    ```

    This will read the Vault secret at path `secret/foo/bar`
    (or `secret/data/foo/bar` if you use Vault KV version 2) and store its
    entirely payload into Chaos Toolkit `mykey`. This means, that all kays
    under that path will be available as-is. For instance, this could be:

    ```
    {
        "mypassword": "shhh",
        "mylogin": "jane
    }
    ```

    You may be more specific as follows:

    ```
    {
        "k8s": {
            "mykey": {
                "type": "vault",
                "path": "foo/bar",
                "key": "mypassword"
            }
        }
    }
    ```

    In that case, `mykey` will be set to the value at `secret/foo/bar` under
    the Vault secret key `mypassword`.
    """

    secret = {}

    client = create_vault_client(configuration)

    if isinstance(secrets_info, dict) and secrets_info.get("type") == "vault":
        if not HAS_HVAC:
            logger.error(
                "Install the `hvac` package to fetch secrets "
                "from Vault: `pip install chaostoolkit-lib[vault]`."
            )
            return {}

        vault_path = secrets_info.get("path")

        if vault_path is None:
            logger.warning(f"Missing Vault secret path for '{secrets_info}'")
            return {}

        # see https://github.com/chaostoolkit/chaostoolkit/issues/98
        kv = client.secrets.kv
        is_kv1 = kv.default_kv_version == "1"
        if is_kv1:
            vault_payload = kv.v1.read_secret(
                path=vault_path,
                mount_point=configuration.get(
                    "vault_secrets_mount_point", "secret"
                ),
            )
        else:
            vault_payload = kv.v2.read_secret_version(
                path=vault_path,
                mount_point=configuration.get(
                    "vault_secrets_mount_point", "secret"
                ),
            )

        if not vault_payload:
            logger.warning(f"No Vault secret found at path: {vault_path}")
            return {}

        if is_kv1:
            data = vault_payload.get("data")
        else:
            data = vault_payload.get("data", {}).get("data")

        key = secrets_info.get("key")

        if key is not None:
            secret = data[key]
        else:
            secret = data

        return secret


###############################################################################
# Internals
###############################################################################
def create_vault_client(configuration: Configuration = None):
    """
    Initialize a Vault client from either a token or an approle.
    """
    client = None
    if HAS_HVAC:
        url = configuration.get("vault_addr")
        client = hvac.Client(url=url)

        client.secrets.kv.default_kv_version = str(
            configuration.get("vault_kv_version", "2")
        )
        logger.debug(
            "Using Vault secrets KV version {}".format(
                client.secrets.kv.default_kv_version
            )
        )

        if "vault_token" in configuration:
            client.token = configuration.get("vault_token")
        elif (
                "vault_role_id" in configuration
                and "vault_role_secret" in configuration
        ):
            role_id = configuration.get("vault_role_id")
            role_secret = configuration.get("vault_role_secret")

            try:
                app_role = client.auth_approle(role_id, role_secret)
            except Exception as ve:
                raise InvalidExperiment(
                    f"Failed to connect to Vault with the AppRole: {str(ve)}"
                )

            client.token = app_role["auth"]["client_token"]
        elif "vault_sa_role" in configuration:
            sa_token_path = (
                    configuration.get("vault_sa_token_path", "")
                    or "/var/run/secrets/kubernetes.io/serviceaccount/token"
            )

            mount_point = configuration.get(
                "vault_k8s_mount_point", "kubernetes"
            )

            try:
                with open(sa_token_path) as sa_token:
                    jwt = sa_token.read()
                    role = configuration.get("vault_sa_role")
                    client.auth_kubernetes(
                        role=role,
                        jwt=jwt,
                        use_token=True,
                        mount_point=mount_point,
                    )
            except OSError:
                raise InvalidExperiment(
                    "Failed to get service account token at: {path}".format(
                        path=sa_token_path
                    )
                )
            except Exception as e:
                raise InvalidExperiment(
                    "Failed to connect to Vault using service account with "
                    "errors: '{errors}'".format(errors=str(e))
                )

    return client
