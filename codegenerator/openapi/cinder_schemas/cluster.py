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


CLUSTER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "binary": {
            "type": "string",
            "description": "The binary name of the services in the cluster.",
        },
        "name": {
            "type": "string",
            "description": "The name of the service cluster.",
        },
        "replication_status": {
            "type": "string",
            "description": "The cluster replication status. Only included in responses if configured.",
            "enum": ["enabled", "disabled"],
        },
        "state": {
            "type": "string",
            "description": "The state of the cluster.",
            "enum": ["up", "down"],
        },
        "status": {
            "type": "string",
            "description": "The status of the cluster.",
            "enum": ["enabled", "disabled"],
        },
    },
}

CLUSTER_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "num_hosts": {
            "type": "integer",
            "description": "The number of hosts in the cluster.",
        },
        "num_down_hosts": {
            "type": "integer",
            "description": "The number of down hosts in the cluster.",
        },
        "last_heartbeat": {
            "type": "string",
            "format": "date-time",
            "description": "The last periodic heartbeat received.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was updated.",
        },
        "disabled_reason": {
            "type": ["string", "null"],
            "description": "The reason for disabling a resource.",
        },
        "frozen": {
            "type": ["boolean", "null"],
            "description": "Whether the cluster is frozen or not.",
            "x-openstack": {"min-ver": "3.26"},
        },
        "active_backend_id": {
            "type": ["string", "null"],
            "description": "The ID of active storage backend. Only in cinder-volume service.",
            "x-openstack": {"min-ver": "3.26"},
        },
        **CLUSTER_SCHEMA["properties"],
    },
}

CLUSTER_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"cluster": CLUSTER_DETAIL_SCHEMA},
}

CLUSTERS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "clusters": {"type": "array", "items": copy.deepcopy(CLUSTER_SCHEMA)}
    },
}

CLUSTER_UPDATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 255,
            "format": "name",
            "description": "The name to identify the service cluster.",
        },
        "binary": {
            "type": ["string", "null"],
            "minLength": 0,
            "maxLength": 255,
            "description": "The binary name of the services in the cluster.",
        },
        "disabled_reason": {
            "type": ["string", "null"],
            "description": "The reason for disabling a resource.",
        },
    },
    "required": ["name"],
    "additionalProperties": False,
}

CLUSTERS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "clusters": {
            "type": "array",
            "items": copy.deepcopy(CLUSTER_DETAIL_SCHEMA),
        }
    },
}

CLUSTERS_LIST_PARAMETERS: dict[str, Any] = {
    "cluster_name": {
        "in": "query",
        "name": "name",
        "description": "Filter the cluster list result by cluster name.",
        "schema": {"type": "string"},
    },
    "cluster_binary": {
        "in": "query",
        "name": "binary",
        "description": "Filter the cluster list result by binary name of the clustered services. One of cinder-api, cinder-scheduler, cinder-volume or cinder-backup.",
        "schema": {
            "type": "string",
            "enum": [
                "cinder-api",
                "cinder-scheduler",
                "cinder-volume",
                "cinder-backup",
            ],
        },
    },
    "cluster_is_up": {
        "in": "query",
        "name": "is_up",
        "description": "Filter the cluster list result by state.",
        "schema": {"type": "boolean"},
    },
    "cluster_disabled": {
        "in": "query",
        "name": "disabled",
        "description": "Filter the cluster list result by status.",
        "schema": {"type": "boolean"},
    },
    "cluster_num_hosts": {
        "in": "query",
        "name": "num_hosts",
        "description": "Filter the cluster list result by number of hosts.",
        "schema": {"type": "number"},
    },
    "cluster_num_down_hosts": {
        "in": "query",
        "name": "num_down_hosts",
        "description": "Filter the cluster list result by number of down hosts.",
        "schema": {"type": "number"},
    },
    "cluster_replication_status": {
        "in": "query",
        "name": "replication_stats",
        "description": "Filter the cluster list result by replication status.",
        "schema": {"type": "string", "enum": ["enabled", "disabled"]},
    },
}

CLUSTERS_LIST_DETAIL_PARAMETERS: dict[str, Any] = {
    "cluster_frozen": {
        "in": "query",
        "name": "frozen",
        "description": "Whether the cluster is frozen or not.",
        "schema": {"type": "boolean"},
        "x-openstack": {"min-ver": "3.26"},
    },
    "cluster_active_backend_id": {
        "in": "query",
        "name": "active_backend_id",
        "description": "The ID of active storage backend. Only in cinder-volume service.",
        "schema": {"type": "string"},
        "x-openstack": {"min-ver": "3.26"},
    },
    **CLUSTERS_LIST_PARAMETERS,
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in ["project_id/clusters:get", "clusters:get"]:
        for key, val in CLUSTERS_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
            ref = f"#/components/parameters/{key}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))

    if operationId in [
        "project_id/clusters/detail:get",
        "clusters/detail:get",
    ]:
        for key, val in CLUSTERS_LIST_DETAIL_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
            ref = f"#/components/parameters/{key}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))


def _get_schema_ref(
    openapi_spec, name, description=None, schema_def=None, action_name=None
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "ClustersDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**CLUSTERS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "ClustersListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**CLUSTERS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "ClusterUpdateRequest":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**CLUSTER_UPDATE_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in ["ClusterShowResponse", "ClusterUpdateResponse"]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**CLUSTER_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
