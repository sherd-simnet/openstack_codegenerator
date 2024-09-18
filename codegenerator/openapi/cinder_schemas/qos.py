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

QOS_SPEC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "consumer": {"type": "string", "description": "The consumer type."},
        "specs": {
            "type": ["object", "null"],
            "description": "A specs object.",
            **parameter_types.extra_specs_with_null,
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The generated ID for the QoS specification.",
        },
        "name": {
            "type": "string",
            "description": "The name of the QoS specification.",
        },
    },
}

QOS_SPEC_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"qos_specs": QOS_SPEC_SCHEMA},
}

QOS_SPECS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"qos_specs": {"type": "array", "items": QOS_SPEC_SCHEMA}},
}

QOS_SPEC_ASSOCIATIONS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "qos_associations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "association_type": {
                        "type": "string",
                        "description": "The QoS association type.",
                    },
                    "id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The Qos association ID.",
                    },
                    "name": {
                        "type": "string",
                        "description": "The QoS association name.",
                    },
                },
                "additionalProperties": False,
                "required": ["association_type", "id", "name"],
            },
        }
    },
}

QOS_SPEC_LIST_PARAMETERS: dict[str, Any] = {
    "qos_spec_sort": {
        "in": "query",
        "name": "sort",
        "description": "Comma-separated list of sort keys and optional sort directions in the form of < key > [: < direction > ]. A valid direction is asc (ascending) or desc (descending).",
        "schema": {"type": "string"},
    },
    "qos_spec_sort_key": {
        "in": "query",
        "name": "sort_key",
        "description": "Sorts by an attribute. A valid value is name, status, container_format, disk_format, size, id, created_at, or updated_at. Default is created_at. The API uses the natural sorting direction of the sort_key attribute value. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "qos_spec_sort_dir": {
        "in": "query",
        "name": "sort_dir",
        "description": "Sorts by one or more sets of attribute and sort direction combinations. If you omit the sort direction in a set, default is desc. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "qos_spec_limit": {
        "in": "query",
        "name": "limit",
        "description": "Requests a page size of items. Returns a number of items up to a limit value. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "integer"},
    },
    "qos_spec_marker": {
        "in": "query",
        "name": "marker",
        "description": "The ID of the last-seen item. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "string"},
    },
    "qos_spec_offset": {
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

    if operationId in ["project_id/qos-specs:get", "qos-specs:get"]:
        for key, val in QOS_SPEC_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
            ref = f"#/components/parameters/{key}"
            if ref not in [x.ref for x in operation_spec.parameters]:
                operation_spec.parameters.append(ParameterSchema(ref=ref))

    if operationId in [
        "project_id/qos-specs/id/disassociate:get",
        "qos-specs/id/disassociate:get",
        "project_id/qos-specs/id/associate:get",
        "qos-specs/id/associate:get",
        "project_id/qos-specs/id/disassociate_all:get",
        "qos-specs/id/disassociate_all:get",
    ]:
        operation_spec.responses["202"] = {"description": "Accepted"}
        operation_spec.responses.pop("200", None)


def _get_schema_ref(
    openapi_spec, name, description=None, schema_def=None, action_name=None
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str

    if name == "Qos_SpecsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**QOS_SPECS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "Qos_SpecsCreateResponse",
        "Qos_SpecShowResponse",
        "Qos_SpecUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**QOS_SPEC_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in ["Qos_SpecsAssociationsResponse"]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**QOS_SPEC_ASSOCIATIONS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"

    else:
        return (None, None, False)

    return (ref, mime_type, True)
