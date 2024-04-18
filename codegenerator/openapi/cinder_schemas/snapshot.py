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

SNAPSHOT_STATUS_ENUM: list[str] = [
    "creating",
    "available",
    "backing-up",
    "deleting",
    "error",
    "deleted",
    "unmanaging",
    "restoring",
    "error_deleting",
]

SNAPSHOT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": SNAPSHOT_STATUS_ENUM,
            "description": "The status for the snapshot.",
        },
        "description": {
            "type": ["string", "null"],
            "description": "A description for the snapshot.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "updated_at": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "The date and time when the resource was updated.",
        },
        "name": {
            "type": ["string", "null"],
            "description": "The name of the object.",
        },
        "volume_id": {
            "type": "string",
            "format": "uuid",
            "description": "If the snapshot was created from a volume, the volume ID.",
        },
        "metadata": copy.deepcopy(common.METADATA_SCHEMA),
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The snapshot UUID.",
        },
        "size": {
            "type": "integer",
            "format": "int64",
            "description": "The size of the volume, in gibibytes (GiB).",
        },
        "count": {
            "type": ["integer", "null"],
            "description": "The total count of requested resource before pagination is applied.",
            "x-openstack": {"min-ver": "3.45"},
        },
    },
    "additionalProperties": False,
    "required": [
        "status",
        "description",
        "created_at",
        "metadata",
        "name",
        "volume_id",
        "id",
        "size",
        "updated_at",
    ],
}

SNAPSHOT_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "os-extended-snapshot-attributes:progress": {
            "type": "string",
            "description": "A percentage value for the build progress.",
        },
        "os-extended-snapshot-attributes:project_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the owning project.",
        },
        "group_snapshot_id": {
            "type": "string",
            "format": "uuid",
            "description": "The ID of the group snapshot.",
            "x-openstack": {"min-ver": "3.14"},
        },
        "consumes_quota": {
            "type": ["boolean", "null"],
            "description": "Whether this resource consumes quota or not. Resources that not counted for quota usage are usually temporary internal resources created to perform an operation.",
            "x-openstack": {"min-ver": "3.65"},
        },
        **SNAPSHOT_SCHEMA["properties"],
    },
}

SNAPSHOT_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A snapshot object.",
    "properties": {"snapshot": copy.deepcopy(SNAPSHOT_DETAIL_SCHEMA)},
    "required": ["snapshot"],
    "additionalProperties": False,
}

SNAPSHOTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of snapshot objects.",
    "properties": {
        "snapshots": {
            "type": "array",
            "items": copy.deepcopy(SNAPSHOT_SCHEMA),
            "description": "A list of volume objects.",
        },
    },
    "required": ["snapshots"],
    "additionalProperties": False,
}

SNAPSHOTS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of snapshot objects.",
    "properties": {
        "snapshots": {
            "type": "array",
            "items": copy.deepcopy(SNAPSHOT_DETAIL_SCHEMA),
            "description": "A list of snapshot objects.",
        },
    },
    "required": ["snapshots"],
    "additionalProperties": False,
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/snapshots:get",
        "snapshots:get",
        "project_id/snapshots/detail:get",
        "snapshots/detail:get",
    ]:
        for pname in [
            "all_tenants",
            "sort",
            "sort_key",
            "sort_dir",
            "limit",
            "offset",
            "marker",
            "with_count",
            "consumes_quota",
        ]:
            ref = f"#/components/parameters/{pname}"
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
    # ### Snapshot
    if name == "SnapshotsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**SNAPSHOTS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    if name == "SnapshotsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**SNAPSHOTS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "SnapshotShowResponse",
        "SnapshotUpdateResponse",
        "SnapshotsCreateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**SNAPSHOT_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    # ### Snapshot Metadata
    elif name in [
        "SnapshotsMetadataListResponse",
        "SnapshotsMetadataUpdate_AllRequest",
        "SnapshotsMetadataUpdate_AllResponse",
        "SnapshotsMetadataCreateRequest",
        "SnapshotsMetadataCreateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**common.METADATA_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "SnapshotsMetadataShowResponse",
        "SnapshotsMetadataUpdateRequest",
        "SnapshotsMetadataUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**common.METADATA_ITEM_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    # Snapshot Actions
    elif name in [
        "SnapshotsActionOs-Reset_StatusResponse",
        "SnapshotsActionOs-Force_DeleteResponse",
        "SnapshotsActionOs-UnmanageResponse",
    ]:
        return (None, None, True)
    else:
        return (None, None, False)

    return (ref, mime_type, True)
