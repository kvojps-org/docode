import json
from typing import Any
import boto3
from botocore.exceptions import ClientError
from decouple import config as decouple_config  # type: ignore
from utils.type_util import cast_to_bool

ENABLE_ENVVAR_OVERRIDE = decouple_config(
    "ENABLE_ENVVAR_OVERRIDE", default=False, cast=bool
)
ssm_client = boto3.client("ssm")
secrets_client = boto3.client("secretsmanager")


def get_param(param_name: str, **kwargs) -> str:
    """Replica a assinatura de 'decouple.config' para uso transparente que suporta EnvVars, SSM e SecretsManager.

    Trata os parâmetros da mesma forma que o decouple. São suportados os parâmetros 'cast'e 'default', que são
    opcionais. Para mínima alteração de chamadas existentes, pode realizar o import da seguinte forma:
    'from infrastructure.environment.env_handler import get_param as config', substituindo o do decouple.
    """
    default = kwargs.get("default", None)
    cast = kwargs.get("cast", str)

    value = _get_param_value(param_name)
    if not value:
        if default is None:
            raise ValueError(
                f"{param_name} não encontrado. Configure o respectivo dado Envvar/SSM/SecretsManager "
                + "ou defina um valor default"
            )
        else:
            value = default

    if value and cast:
        if cast == bool:
            cast = cast_to_bool
        value = cast(value)

    return value


def _get_param_value(param_key: str) -> Any:
    """Procura e retorna valor definido do parâmetro solicitado em EnvVars, SSM e SecretsManager, que pode ser None"""
    if ENABLE_ENVVAR_OVERRIDE:
        return _get_env_var_value(param_key)

    return _get_aws_param_value(param_key)


def _get_env_var_value(param_key: str) -> str:
    return decouple_config(param_key, default="", cast=str)


def _get_aws_param_value(param_key: str) -> Any:
    secrets = _get_secret_env_vars()

    if param_key in secrets:
        secret_param = secrets[param_key]
        secret_param_name, prop = secret_param.split(sep=":", maxsplit=1)
        ssm_error = ValueError(
            f"Erro ao obter valor do parâmetro SecretsManager '{secret_param_name}'"
        )
        try:
            secret_value = secrets_client.get_secret_value(SecretId=secret_param_name)
            if not isinstance(secret_value, dict):
                raise ssm_error
            secret_string = secret_value.get("SecretString", None)
            if secret_string is None:
                raise ssm_error
            try:
                payload = json.loads(secret_string)
                if not isinstance(payload, dict):
                    raise ssm_error
                return payload.get(prop, None)
            except json.JSONDecodeError:
                raise ssm_error
        except ClientError:
            raise ssm_error


def _get_secret_env_vars() -> dict[str, str]:
    env_name = decouple_config("ENV_NAME", cast=str)

    return {
        "GEMINI_API_KEY": f"gemini-{env_name}:api_key",
    }


if __name__ == "__main__":

    def _test_get_param(param: str, **kwargs) -> None:
        print(f"{param} (decouple): {decouple_config(param, **kwargs)}")
        print(f"{param} (params): {get_param(param, **kwargs)}")

    def _run_tests() -> None:
        _test_get_param("GEMINI_API_KEY")

    _run_tests()
