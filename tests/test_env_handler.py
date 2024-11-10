from unittest.mock import patch
import pytest
from core.infrastructure.environment.env_handler import get_param


@patch(
    "core.infrastructure.environment.env_handler._get_env_var_value",
    return_value="localhost",
)
@patch(
    "core.infrastructure.environment.env_handler._get_aws_param_value",
    return_value="rds_db_host",
)
@patch("core.infrastructure.environment.env_handler.ENABLE_ENVVAR_OVERRIDE", True)
def test_get_overridden_environment_variable(
    mock_env_var_value,
    mock_aws_param_value,
    param_key="POSTGRES_HOST",
    env_param_value="localhost",
):
    assert get_param(param_key) == env_param_value


@patch(
    "core.infrastructure.environment.env_handler._get_env_var_value",
    return_value="localhost",
)
@patch(
    "core.infrastructure.environment.env_handler._get_aws_param_value",
    return_value="rds_db_host",
)
@patch("core.infrastructure.environment.env_handler.ENABLE_ENVVAR_OVERRIDE", False)
def test_get_aws_environment_variable(
    mock_env_var_value,
    mock_aws_param_value,
    param_key="POSTGRES_HOST",
    aws_param_value="rds_db_host",
):
    assert get_param(param_key) == aws_param_value


@patch(
    "core.infrastructure.environment.env_handler._get_param_value",
    return_value="localhost",
)
def test_get_environment_variable_with_value_and_default_value_returns_value(
    mock_param_value, param_key="POSTGRES_HOST"
):
    assert get_param(param_key, default="default") == "localhost"


@patch(
    "core.infrastructure.environment.env_handler._get_param_value",
    return_value=None,
)
def test_get_environment_variable_only_with_default_value_returns_default_value(
    mock_param_value, param_key="POSTGRES_HOST"
):
    assert get_param(param_key, default="default") == "default"


@patch(
    "core.infrastructure.environment.env_handler._get_param_value",
    return_value=None,
)
def test_get_environment_variable_without_any_value_throws_value_error(
    mock_param_value, param_key="POSTGRES_HOST"
):
    with pytest.raises(ValueError):
        get_param(param_key)
