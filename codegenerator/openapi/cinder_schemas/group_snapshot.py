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

GROUP_SNAPSHOT_LIST_PARAMETERS: dict[str, Any] = {
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

GROUP_SNAPSHOT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A volume group snapshot object.",
    "properties": {
        "name": {
            "type": ["string", "null"],
            "description": "The group snapshot name.",
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the group snapshot.",
        },
    },
}

GROUP_SNAPSHOT_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A group snapshot bject.",
    "properties": {
        "status": {
            "type": "string",
            "description": "The status of the generic group snapshot.",
        },
        "description": {
            "type": ["string", "null"],
            "description": "The group snapshot description.",
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
        "group_id": {
            "type": "string",
            "format": "uuid",
            "description": "The ID of the group.",
        },
        "group_type_id": {
            "type": "string",
            "format": "uuid",
            "description": "The group type ID.",
        },
        "project_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "The UUID of the volume group project.",
            "x-openstack": {"min-ver": "3.58"},
        },
        **GROUP_SNAPSHOT_SCHEMA["properties"],
    },
}

GROUP_SNAPSHOTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of group snapshot objects.",
    "properties": {
        "group_snapshots": {
            "type": "array",
            "items": copy.deepcopy(GROUP_SNAPSHOT_SCHEMA),
        }
    },
}

GROUP_SNAPSHOTS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of group snapshot objects.",
    "properties": {
        "group_snapshots": {
            "type": "array",
            "items": copy.deepcopy(GROUP_SNAPSHOT_DETAIL_SCHEMA),
        }
    },
}

GROUP_SNAPSHOT_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"group_snapshot": GROUP_SNAPSHOT_DETAIL_SCHEMA},
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/group_snapshots:get",
        "group_snapshots:get",
        "project_id/group_snapshots/detail:get",
        "group_snapshots/detail:get",
    ]:
        for key, val in GROUP_SNAPSHOT_LIST_PARAMETERS.items():
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
    if name == "Group_SnapshotsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUP_SNAPSHOTS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Group_SnapshotsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUP_SNAPSHOTS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "Group_SnapshotsCreateResponse",
        "Group_SnapshotShowResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**GROUP_SNAPSHOT_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
