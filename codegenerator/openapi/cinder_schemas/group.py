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

from codegenerator.openapi.cinder_schemas import common
from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema

GROUP_LIST_PARAMETERS: dict[str, Any] = {
    "group_all_tenants": {
        "in": "query",
        "name": "all_tenants",
        "description": "Shows details for all project. Admin only.",
        "schema": {"type": "boolean"},
    },
    "group_sort": {
        "in": "query",
        "name": "sort",
        "description": "Comma-separated list of sort keys and optional sort directions in the form of < key > [: < direction > ]. A valid direction is asc (ascending) or desc (descending).",
        "schema": {"type": "string"},
    },
    "group_sort_key": {
        "in": "query",
        "name": "sort_key",
        "description": "Sorts by an attribute. A valid value is name, status, container_format, disk_format, size, id, created_at, or updated_at. Default is created_at. The API uses the natural sorting direction of the sort_key attribute value. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "group_sort_dir": {
        "in": "query",
        "name": "sort_dir",
        "description": "Sorts by one or more sets of attribute and sort direction combinations. If you omit the sort direction in a set, default is desc. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "group_limit": {
        "in": "query",
        "name": "limit",
        "description": "Requests a page size of items. Returns a number of items up to a limit value. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "integer"},
    },
    "group_marker": {
        "in": "query",
        "name": "marker",
        "description": "The ID of the last-seen item. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "string"},
    },
    "group_offset": {
        "in": "query",
        "name": "offset",
        "description": "Used in conjunction with limit to return a slice of items. offset is where to start in the list.",
        "schema": {"type": "integer"},
    },
}

GROUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A volume group object.",
    "properties": {
        "name": {
            "type": ["string", "null"],
            "description": "The group name.",
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the group.",
        },
    },
}

GROUP_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A group object.",
    "properties": {
        "status": {
            "type": "string",
            "description": "The status of the generic group.",
        },
        "description": {
            "type": ["string", "null"],
            "description": "The group description.",
        },
        "availability_zone": {
            "type": "string",
            "description": "The name of the availability zone.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "group_type": {
            "type": "string",
            "format": "uuid",
            "description": "The group type ID.",
        },
        "group_snapshot_id": {
            "type": ["string", "null"],
            "description": "The ID of the group snapshot.",
        },
        "source_group_id": {
            "type": ["string", "null"],
            "description": "The UUID of the source group.",
        },
        "volume_types": {
            "type": "array",
            "items": {
                "type": "string",
                "format": "uuid",
                "description": "The ID of the volume type.",
            },
            "description": "The list of volume types. In an environment with multiple-storage back ends, the scheduler determines where to send the volume based on the volume type. ",
        },
        "volumes": {
            "type": "array",
            "items": {"type": "string", "format": "uuid", "description": ""},
            "description": "A list of volume ids, available only when list_volume set true.",
            "x-openstack": {"min-ver": "3.25"},
        },
        "replication_status": {
            "type": ["string", "null"],
            "description": "The group replication status.",
            "x-openstack": {"min-ver": "3.38"},
        },
        "project_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "The UUID of the volume group project.",
            "x-openstack": {"min-ver": "3.58"},
        },
        **GROUP_SCHEMA["properties"],
    },
}

GROUPS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of group objects.",
    "properties": {
        "groups": {
            "type": "array",
            "items": copy.deepcopy(GROUP_SCHEMA),
        },
    },
}

GROUPS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of group objects.",
    "properties": {
        "groups": {
            "type": "array",
            "items": copy.deepcopy(GROUP_DETAIL_SCHEMA),
        },
    },
}

GROUP_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"group": GROUP_DETAIL_SCHEMA},
}

GROUP_RECORD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "backup-record": {
            "type": "object",
            "description": "An object recording volume backup metadata, including backup_service and backup_url.",
            "properties": {
                "backup_service": {
                    "type": "string",
                    "description": "The service used to perform the backup.",
                },
                "backup_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "An identifier string to locate the backup.",
                },
            },
        }
    },
}

GROUP_REPLICATION_TARGETS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "backend_id": {
            "type": "string",
            "format": "uuid",
            "description": "ID of failover target backend.",
        },
        "unique_key": {
            "type": ["string", "null"],
            "description": "Vendor specific key-values. Only returned if administrator.",
        },
    },
    "required": ["backend_id"],
    "additionalProperties": False,
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/groups:get",
        "groups:get",
        "project_id/groups/detail:get",
        "groups/detail:get",
    ]:
        for key, val in GROUP_LIST_PARAMETERS.items():
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
    if name == "GroupsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUPS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "GroupsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUPS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "GroupsCreateResponse",
        "GroupsShowResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUP_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "GroupsActionList_Replication_TargetsResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUP_REPLICATION_TARGETS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "GroupsActionReset_StatusResponse",
        "GroupsActionDeleteResponse",
        "GroupsActionEnable_ReplicationResponse",
        "GroupsActionDisable_ReplicationResponse",
        "GroupsActionFailover_ReplicationResponse",
    ]:
        return (None, None, True)
    else:
        return (None, None, False)

    return (ref, mime_type, True)
