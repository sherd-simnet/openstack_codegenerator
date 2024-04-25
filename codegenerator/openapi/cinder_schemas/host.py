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
import copy
from typing import Any

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema

HOST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "service-status": {
            "type": "string",
            "enum": ["available", "unavailable"],
            "description": "The status of the service. One of available or unavailable.",
        },
        "service": {
            "type": "string",
            "description": "The name of the service which is running on the host.",
        },
        "zone": {
            "type": "string",
            "description": "The availability zone name.",
        },
        "service-state": {
            "type": "string",
            "enum": ["enabled", "disabled"],
            "description": "The state of the service. One of enabled or disabled.",
        },
        "host_name": {
            "type": "string",
            "description": "The name of the host that hosts the storage backend, may take the format of host@backend.",
        },
        "last-update": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "The date and time when the resource was updated.",
        },
    },
    "additionalProperties": False,
    "required": [
        "service-status",
        "service",
        "zone",
        "service-state",
        "host_name",
        "last-update",
    ],
}

HOST_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A host object.",
    "properties": {
        "resource": {
            "type": "object",
            "properties": {
                "volume_count": {
                    "type": "string",
                    "description": "Total number of volumes.",
                },
                "total_volume_gb": {
                    "type": "string",
                    "description": "The total number of gibibytes (GiB) used.",
                },
                "total_snapshot_gb": {
                    "type": "string",
                    "description": "The total number of gibibytes (GiB) used by snapshots.",
                },
                "project": {
                    "type": "string",
                    "description": "The Project ID which the host resource belongs to. In the summary resource, the value is (total).",
                },
                "host": {
                    "type": "string",
                    "description": "The name of the host that hosts the storage backend, may take the format of host@backend.",
                },
                "snapshot_count": {
                    "type": "string",
                    "description": "The total number of snapshots used.",
                },
            },
            "additionalProperties": False,
            "required": [
                "volume_count",
                "total_volume_gb",
                "total_snapshot_gb",
                "project",
                "host",
                "snapshot_count",
            ],
        }
    },
    "additionalProperties": False,
    "required": ["resource"],
}

HOSTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of host objects.",
    "properties": {
        "hosts": {
            "type": "array",
            "items": copy.deepcopy(HOST_SCHEMA),
        },
    },
}

HOSTS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of host objects.",
    "properties": {
        "hosts": {
            "type": "array",
            "items": copy.deepcopy(HOST_DETAIL_SCHEMA),
        },
    },
}

HOST_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "host": {"type": "array", "items": HOST_DETAIL_SCHEMA},
    },
}


def _get_schema_ref(
    openapi_spec,
    name,
    description=None,
    schema_def=None,
    action_name=None,
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "Os_HostsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**HOSTS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Os_HostShowResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**HOST_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
