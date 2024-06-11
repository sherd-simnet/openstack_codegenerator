#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from typing import Any

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema


DOMAIN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A domain object",
    "properties": {
        "id": {"type": "string", "format": "uuid", "readOnly": True},
        "name": {
            "type": "string",
            "description": "The name of the domain.",
            "minLength": 1,
            "maxLength": 255,
            "pattern": r"[\S]+",
        },
        "description": {
            "type": "string",
            "description": "The description of the domain.",
        },
        "enabled": {
            "type": "boolean",
            "description": "If set to true, domain is enabled. If set to false, domain is disabled.",
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[^,/]*$",
                "minLength": 1,
                "maxLength": 255,
            },
        },
        "options": {
            "type": "object",
            "description": "The resource options for the domain. Available resource options are immutable.",
        },
    },
}

DOMAIN_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"domain": DOMAIN_SCHEMA},
}

DOMAINS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"domains": {"type": "array", "items": DOMAIN_SCHEMA}},
}

DOMAIN_CONFIGS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "description": "A config object.",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": True,
            },
        }
    },
}

DOMAIN_CONFIG_GROUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "description": "A config object.",
            "additionalProperties": {
                "type": "object",
                "additionalProperties": True,
            },
            "maxProperties": 1,
        }
    },
}

DOMAIN_CONFIG_GROUP_OPTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "config": {
            "type": "object",
            "additionalProperties": True,
            "maxProperties": 1,
        }
    },
}

DOMAIN_LIST_PARAMETERS: dict[str, dict] = {
    "domain_name": {
        "in": "query",
        "name": "name",
        "description": "Filters the response by a domain name.",
        "schema": {"type": "string"},
    },
    "domain_enabled": {
        "in": "query",
        "name": "enabled",
        "description": "If set to true, then only domains that are enabled will be returned, if set to false only that are disabled will be returned. Any value other than 0, including no value, will be interpreted as true.",
        "schema": {"type": "boolean"},
    },
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""

    operationId = operation_spec.operationId
    if operationId == "domains:get":
        for (
            key,
            val,
        ) in DOMAIN_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
            ref = f"#/components/parameters/{key}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))


def _get_schema_ref(
    openapi_spec,
    name,
    description=None,
    schema_def=None,
    action_name=None,
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    # Domains
    if name in [
        "DomainsPostRequest",
        "DomainsPostResponse",
        "DomainGetResponse",
        "DomainPatchRequest",
        "DomainPatchResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            "Domain", TypeSchema(**DOMAIN_CONTAINER_SCHEMA)
        )
        ref = "#/components/schemas/Domain"
    elif name == "DomainsGetResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**DOMAINS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"

    # Domain Config
    elif name in [
        "DomainsConfigDefaultGetResponse",
        "DomainsConfigGetResponse",
        "DomainsConfigPutRequest",
        "DomainsConfigPutResponse",
        "DomainsConfigPatchResponse",
        "DomainsConfigPatchRequest",
        "DomainsConfigPatchResponse",
        "DomainsConfigDefaultGetResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            "DomainConfig",
            TypeSchema(**DOMAIN_CONFIGS_SCHEMA),
        )
        ref = "#/components/schemas/DomainConfig"
    elif name in [
        "DomainsConfigDefaultGroupGetResponse",
        "DomainsConfigGroupGetResponse",
        "DomainsConfigGroupPatchRequest",
        "DomainsConfigGroupPatchResponse",
        "DomainsConfigGroupPatchResponse",
        "DomainsConfigGroupPatchResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            "DomainConfigGroup",
            TypeSchema(**DOMAIN_CONFIG_GROUP_SCHEMA),
        )
        ref = "#/components/schemas/DomainConfigGroup"

    elif name in [
        "DomainsConfigDefaultGroupOptionGetResponse",
        "DomainsConfigGroupOptionPatchRequest",
        "DomainsConfigGroupOptionPatchResponse",
        "DomainsConfigGroupOptionGetResponse",
        "DomainsConfigGroupOptionPatchRequest",
    ]:
        openapi_spec.components.schemas.setdefault(
            "DomainConfigGroupOption",
            TypeSchema(**DOMAIN_CONFIG_GROUP_OPTION_SCHEMA),
        )
        ref = "#/components/schemas/DomainConfigGroupOption"

    else:
        return (None, None, False)

    return (ref, mime_type, True)
