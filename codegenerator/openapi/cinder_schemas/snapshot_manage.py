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

from cinder.api.schemas import snapshot_manage as cinder_snapshot_manage

from codegenerator.openapi.cinder_schemas import snapshot

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema

MANAGEABLE_SNAPSHOT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "source_reference": {
            "type": "object",
            "properties": {
                "source-name": {
                    "type": "string",
                    "description": "The resource's name.",
                }
            },
        },
        "safe_to_manage": {
            "type": ["boolean", "null"],
            "description": "If the resource can be managed or not.",
        },
        "reference": {
            "type": "object",
            "description": "Some information for the resource.",
            "properties": {
                "source-name": {
                    "type": "string",
                    "description": "The resource’s name.",
                }
            },
        },
        "size": {
            "type": "integer",
            "format": "int64",
            "description": "The size of the volume, in gibibytes (GiB).",
        },
    },
    "additionalProperties": False,
    "required": ["source_reference", "safe_to_manage", "reference", "size"],
}

MANAGEABLE_SNAPSHOT_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "cinder_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "The UUID of the resource in Cinder.",
        },
        "reason_not_safe": {
            "type": ["string", "null"],
            "description": "The reason why the resource can’t be managed.",
        },
        "extra_info": {
            "type": ["string", "null"],
            "description": "More information about the resource.",
        },
        **MANAGEABLE_SNAPSHOT_SCHEMA["properties"],
    },
}

MANAGEABLE_SNAPSHOTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manageable-snapshots": {
            "type": "array",
            "items": MANAGEABLE_SNAPSHOT_SCHEMA,
        }
    },
}

MANAGEABLE_SNAPSHOTS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manageable-snapshots": {
            "type": "array",
            "items": MANAGEABLE_SNAPSHOT_DETAIL_SCHEMA,
        }
    },
}

# NOTE(gtema): cinder create schema is broken and require sanity
MANAGEABLE_SNAPSHOT_CREATE_REQUEST_SCHEMA: dict[str, Any] = copy.deepcopy(
    cinder_snapshot_manage.create
)
MANAGEABLE_SNAPSHOT_CREATE_REQUEST_SCHEMA["properties"].pop("type", None)


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/manageable_snapshots/detail:get",
        "manageable_snapshots/detail:get",
        "project_id/manageable_snapshots:get",
        "manageable_snapshots:get",
    ]:
        for pname in [
            "sort",
            "sort_key",
            "sort_dir",
            "limit",
            "offset",
            "marker",
        ]:
            ref = f"#/components/parameters/{pname}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))


def _get_schema_ref(
    openapi_spec, name, description=None, schema_def=None, action_name=None
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    # ### Snapshot
    if name == "Manageable_SnapshotsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MANAGEABLE_SNAPSHOTS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    if name == "Manageable_SnapshotsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MANAGEABLE_SNAPSHOTS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Manageable_SnapshotsCreateRequest":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MANAGEABLE_SNAPSHOT_CREATE_REQUEST_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Manageable_SnapshotsCreateResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**snapshot.SNAPSHOT_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
