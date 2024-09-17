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

from codegenerator.common.schema import TypeSchema
from codegenerator.common.schema import ParameterSchema
from codegenerator.openapi.cinder_schemas import common


MESSAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "request_id": {
            "type": "string",
            "description": "The id of the request during which the message was created.",
        },
        "message_level": {
            "type": "string",
            "description": "The level of the message, possible value is only ‘ERROR’ now.",
        },
        "links": common.LINKS_SCHEMA,
        "event_id": {
            "type": "string",
            "description": "The id of the event to this message, this id could eventually be translated into user_message.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created.",
        },
        "guaranteed_until": {
            "type": "string",
            "format": "date-time",
            "description": "The expire time of the message, this message could be deleted after this time.",
        },
        "resource_uuid": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the resource during whose operation the message was created.",
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID for the message.",
        },
        "resource_type": {
            "type": "string",
            "description": "The resource type corresponding to resource_uuid.",
        },
        "user_message": {
            "type": "string",
            "description": "The translated readable message corresponding to event_id.",
        },
    },
    "additionalProperties": False,
    "required": [
        "request_id",
        "message_level",
        "event_id",
        "created_at",
        "id",
        "user_message",
    ],
}

MESSAGES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"messages": {"type": "array", "items": MESSAGE_SCHEMA}},
    "additionalProperties": False,
    "required": ["messages"],
}

MESSAGE_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"message": MESSAGE_SCHEMA},
    "additionalProperties": False,
    "required": ["message"],
}


def _post_process_operation_hook(openapi_spec, operation_spec, path: str | None = None):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/messages:get",
        "messages:get",
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
    if name == "MessagesListResponse":
        openapi_spec.components.schemas.setdefault(name, TypeSchema(**MESSAGES_SCHEMA))
        ref = f"#/components/schemas/{name}"
    if name == "MessageShowResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**MESSAGE_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
