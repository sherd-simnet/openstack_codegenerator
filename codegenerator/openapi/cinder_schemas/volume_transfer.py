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
from codegenerator.openapi.cinder_schemas import common


VOLUME_TRANSFER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the volume transfer.",
        },
        "links": common.LINKS_SCHEMA,
        "name": {
            "type": ["string", "null"],
            "description": "The name of the object.",
        },
        "volume_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the volume.",
        },
    },
}

OS_VOLUME_TRANSFER_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        **VOLUME_TRANSFER_SCHEMA["properties"],
    },
}

VOLUME_TRANSFER_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "destination_project_id": {
            "type": "string",
            "format": "uuid",
            "description": "Records the destination project_id after volume transfer.",
            "x-openstack": {"min-ver": "3.57"},
        },
        "source_project_id": {
            "type": "string",
            "format": "uuid",
            "description": "Records the source project_id before volume transfer.",
            "x-openstack": {"min-ver": "3.57"},
        },
        "accepted": {
            "type": "boolean",
            "description": "Records if this transfer was accepted or not.",
            "x-openstack": {"min-ver": "3.57"},
        },
        "no_snapshots": {
            "type": "boolean",
            "description": "Transfer volume without snapshots. Defaults to False if not specified.",
            "x-openstack": {"min-ver": "3.55"},
        },
        **VOLUME_TRANSFER_SCHEMA["properties"],
    },
}


OS_VOLUME_TRANSFER_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"transfer": OS_VOLUME_TRANSFER_DETAIL_SCHEMA},
}

VOLUME_TRANSFER_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"transfer": VOLUME_TRANSFER_DETAIL_SCHEMA},
}

VOLUME_TRANSFERS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "transfers": {"type": "array", "items": VOLUME_TRANSFER_SCHEMA}
    },
}

OS_VOLUME_TRANSFERS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "transfers": {
            "type": "array",
            "items": OS_VOLUME_TRANSFER_DETAIL_SCHEMA,
        }
    },
}

VOLUME_TRANSFERS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "transfers": {"type": "array", "items": VOLUME_TRANSFER_DETAIL_SCHEMA}
    },
}

VOLUME_TRANSFER_LIST_PARAMETERS: dict[str, Any] = {
    "transfer_is_public": {
        "in": "query",
        "name": "is_public",
        "description": "Filter the volume transfer by public visibility.",
        "schema": {"type": "boolean"},
    },
    "transfer_all_tenants": {
        "in": "query",
        "name": "all_tenants",
        "description": "Shows details for all project. Admin only.",
        "schema": {"type": "boolean"},
    },
    "transfer_sort": {
        "in": "query",
        "name": "sort",
        "description": "Comma-separated list of sort keys and optional sort directions in the form of < key > [: < direction > ]. A valid direction is asc (ascending) or desc (descending).",
        "schema": {"type": "string"},
    },
    "transfer_sort_key": {
        "in": "query",
        "name": "sort_key",
        "description": "Sorts by an attribute. A valid value is name, status, container_format, disk_format, size, id, created_at, or updated_at. Default is created_at. The API uses the natural sorting direction of the sort_key attribute value. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "transfer_sort_dir": {
        "in": "query",
        "name": "sort_dir",
        "description": "Sorts by one or more sets of attribute and sort direction combinations. If you omit the sort direction in a set, default is desc. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "transfer_limit": {
        "in": "query",
        "name": "limit",
        "description": "Requests a page size of items. Returns a number of items up to a limit value. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "integer"},
    },
    "transfer_marker": {
        "in": "query",
        "name": "marker",
        "description": "The ID of the last-seen item. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "string"},
    },
    "transfer_offset": {
        "in": "query",
        "name": "offset",
        "description": "Used in conjunction with limit to return a slice of items. offset is where to start in the list.",
        "schema": {"type": "integer"},
    },
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId

    if operationId in [
        "project_id/volume-transfers/detail:get",
        "volume-transfers/detail:get",
    ]:
        for key, val in VOLUME_TRANSFER_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
            ref = f"#/components/parameters/{key}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))
    if operationId in [
        "project_id/os-volume-transfers/detail:get",
        "os-volume-transfers/detail:get",
    ]:
        # OS-VOLUME-TRANSFERS supports only "all_tenants" QP. Skip separate
        # structure and just copy single param.
        key = "transfer_all_tenants"
        val = VOLUME_TRANSFER_LIST_PARAMETERS[key]
        openapi_spec.components.parameters.setdefault(
            key, ParameterSchema(**val)
        )
        ref = f"#/components/parameters/{key}"
        if ref not in [x.ref for x in operation_spec.parameters]:
            operation_spec.parameters.append(ParameterSchema(ref=ref))
    if path and "volume-transfers" in path:
        operation_spec.openstack.setdefault("min-ver", "3.55")


def _get_schema_ref(
    openapi_spec, name, description=None, schema_def=None, action_name=None
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str

    if name == "Os_Volume_TransferListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**VOLUME_TRANSFERS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Os_Volume_TransferDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**OS_VOLUME_TRANSFERS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "Os_Volume_TransferCreateResponse",
        "Os_Volume_TransferAcceptResponse",
        "Os_Volume_TransferShowResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**OS_VOLUME_TRANSFER_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"

    elif name == "Volume_TransfersListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**VOLUME_TRANSFERS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Volume_TransfersDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**VOLUME_TRANSFERS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "Volume_TransfersCreateResponse",
        "Volume_TransfersAcceptResponse",
        "Volume_TransferShowResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**VOLUME_TRANSFER_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"

    else:
        return (None, None, False)

    return (ref, mime_type, True)
