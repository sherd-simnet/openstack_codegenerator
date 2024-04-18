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

from cinder.api.schemas import volume_manage

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema
from codegenerator.openapi.cinder_schemas import volume


MANAGEABLE_VOLUME_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Manageable volume object.",
    "properties": {
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
}

MANAGEABLE_VOLUME_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Manageable volume object.",
    "properties": {
        "cinder_id": {
            "type": "string",
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
        **MANAGEABLE_VOLUME_SCHEMA,
    },
}

MANAGEABLE_VOLUMES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manageable-volumes": {
            "type": "array",
            "items": MANAGEABLE_VOLUME_SCHEMA,
        }
    },
}

MANAGEABLE_VOLUMES_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manageable-volumes": {
            "type": "array",
            "items": MANAGEABLE_VOLUME_DETAIL_SCHEMA,
        }
    },
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/manageable_volumes/detail:get",
        "manageable_volumes/detail:get",
        "project_id/manageable_volumes:get",
        "manageable_volumes:get",
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
    openapi_spec,
    name,
    description=None,
    schema_def=None,
    action_name=None,
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "Manageable_VolumesDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MANAGEABLE_VOLUMES_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Manageable_VolumesListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MANAGEABLE_VOLUMES_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Manageable_VolumesCreateRequest":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**volume_manage.volume_manage_create)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Manageable_VolumesCreateResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**volume.VOLUME_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
