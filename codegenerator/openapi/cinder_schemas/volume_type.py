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

from cinder.api.validation import parameter_types

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import TypeSchema

VOLUME_TYPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
            "description": "The volume type description.",
        },
        "extra_specs": {
            "description": "A key and value pair that contains additional specifications that are associated with the volume type. Examples include capabilities, capacity, compression, and so on, depending on the storage driver in use.",
            **parameter_types.extra_specs_with_no_spaces_key,
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the volume type.",
        },
        "is_public": {
            "type": "boolean",
            "description": "Whether the volume type is publicly visible.",
        },
        "name": {
            "type": "string",
            "description": "The volume type description.",
        },
        "os-volume-type-access:is_public": {
            "type": "boolean",
            "description": "Whether the volume type is publicly visible.",
        },
        "qos_specs_id": {
            "type": "string",
            "format": "uuid",
            "description": "The QoS specifications ID.",
        },
    },
}

VOLUME_TYPE_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"volume_type": VOLUME_TYPE_SCHEMA},
}

VOLUME_TYPES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"volume_types": {"type": "array", "items": VOLUME_TYPE_SCHEMA}},
}

VOLUME_TYPE_LIST_PARAMETERS: dict[str, Any] = {
    "type_is_public": {
        "in": "query",
        "name": "is_public",
        "description": "Filter the volume type by public visibility.",
        "schema": {"type": "boolean"},
    },
    "type_sort": {
        "in": "query",
        "name": "sort",
        "description": "Comma-separated list of sort keys and optional sort directions in the form of < key > [: < direction > ]. A valid direction is asc (ascending) or desc (descending).",
        "schema": {"type": "string"},
    },
    "type_sort_key": {
        "in": "query",
        "name": "sort_key",
        "description": "Sorts by an attribute. A valid value is name, status, container_format, disk_format, size, id, created_at, or updated_at. Default is created_at. The API uses the natural sorting direction of the sort_key attribute value. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "type_sort_dir": {
        "in": "query",
        "name": "sort_dir",
        "description": "Sorts by one or more sets of attribute and sort direction combinations. If you omit the sort direction in a set, default is desc. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "type_limit": {
        "in": "query",
        "name": "limit",
        "description": "Requests a page size of items. Returns a number of items up to a limit value. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "integer"},
    },
    "type_marker": {
        "in": "query",
        "name": "marker",
        "description": "The ID of the last-seen item. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "string"},
    },
    "type_offset": {
        "in": "query",
        "name": "offset",
        "description": "Used in conjunction with limit to return a slice of items. offset is where to start in the list.",
        "schema": {"type": "integer"},
    },
}

VOLUME_TYPE_EXTRA_SPECS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "extra_specs": {
            "description": "A key and value pair that contains additional specifications that are associated with the volume type. Examples include capabilities, capacity, compression, and so on, depending on the storage driver in use.",
            **parameter_types.extra_specs_with_no_spaces_key,
        },
    },
}

VOLUME_TYPE_EXTRA_SPEC_SCHEMA: dict[str, Any] = (
    parameter_types.extra_specs_with_no_spaces_key
)

VOLUME_TYPE_ACCESS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "volume_type_access": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the project.",
                    },
                    "volume_type_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The UUID of the volume type.",
                    },
                },
            },
        }
    },
}

VOLUME_TYPE_ENCRYPTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "cipher": {
            "type": "string",
            "description": "The encryption algorithm or mode. For example, aes-xts-plain64. The default value is None.",
        },
        "control_location": {
            "type": "string",
            "enum": ["front-end", "back-end"],
            "description": "Notional service where encryption is performed. Valid values are “front-end” or “back-end”. The default value is “front-end”.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "deleted": {
            "type": "boolean",
            "description": "The resource is deleted or not.",
        },
        "deleted_at": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "The date and time when the resource was deleted.",
        },
        "encryption_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the encryption.",
        },
        "key_size": {
            "type": "integer",
            "description": "Size of encryption key, in bits. This is usually 256. The default value is None.",
        },
        "provider": {
            "type": "string",
            "description": "The class that provides encryption support.",
        },
        "updated_at": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "The date and time when the resource was updated.",
        },
    },
}

VOLUME_TYPE_ENCRYPTION_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"encryption": VOLUME_TYPE_ENCRYPTION_SCHEMA},
}

VOLUME_TYPE_ENCRYPTION_SHOW_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "cipher": {
            "type": "string",
            "description": "The encryption algorithm or mode. For example, aes-xts-plain64. The default value is None.",
        },
    },
}

DEFAULT_TYPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "project_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the project.",
        },
        "volume_type_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID for an existing volume type.",
        },
    },
}

DEFAULT_TYPES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"default_types": {"type": "array", "items": DEFAULT_TYPE_SCHEMA}},
}

DEFAULT_TYPE_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"default_type": DEFAULT_TYPE_SCHEMA},
}


def _post_process_operation_hook(openapi_spec, operation_spec, path: str | None = None):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId

    if operationId in [
        "project_id/types:get",
    ]:
        for key, val in VOLUME_TYPE_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(key, ParameterSchema(**val))
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

    # ### Volume Type
    if name == "TypesListResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPES_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "TypesCreateResponse",
        "TypeShowResponse",
        "TypeUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_CONTAINER_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "TypesExtra_SpecsListResponse",
        "TypesExtra_SpecsCreateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_EXTRA_SPECS_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"

    elif name in [
        "TypesExtra_SpecShowResponse",
        "TypesExtra_SpecUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_EXTRA_SPEC_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"

    elif name == "TypesOs_Volume_Type_AccessListResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_ACCESS_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "TypesActionAddprojectaccessResponse",
        "TypesActionRemoveprojectaccessResponse",
    ]:
        return (None, None, True)

    # ### Volume Type Encryption
    # this is not really a list operation, but who cares
    elif name == "TypesEncryptionListResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_ENCRYPTION_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name == "TypesEncryptionShowResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_ENCRYPTION_SHOW_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "TypesEncryptionCreateResponse",
        "TypesEncryptionUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**VOLUME_TYPE_ENCRYPTION_CONTAINER_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name == "Default_TypesListResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**DEFAULT_TYPES_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"

    elif name in [
        "Default_TypeCreate_UpdateResponse",
        "Default_TypeDetailResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**DEFAULT_TYPE_CONTAINER_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"

    else:
        return (None, None, False)

    return (ref, mime_type, True)
