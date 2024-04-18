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


ATTACHMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The ID of attachment.",
        },
        "instance": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "The UUID of the attaching instance.",
        },
        "volume_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the volume which the attachment belongs to.",
        },
        "status": {
            "type": "string",
            "description": "The status of the attachment.",
            "enum": [
                "attached",
                "attaching",
                "detached",
                "reserved",
                "error_attaching",
                "error_detaching",
                "deleted",
            ],
        },
    },
}

ATTACHMENT_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "attach_mode": {
            "type": "string",
            "description": "The attach mode of attachment, read-only (‘ro’) or read-and-write (‘rw’), default is ‘rw’.",
            "enum": ["ro", "rw"],
            "x-openstack": {"min-ver": "3.54"},
        },
        "attached_at": {
            "type": "string",
            "format": "date-time",
            "description": "The time when attachment is attached.",
        },
        "connecttion_info": {
            "type": "object",
            "description": "The connection info used for server to connect the volume.",
        },
        "detached_at": {
            "type": "string",
            "format": "date-time",
            "description": "The time when attachment is detached.",
        },
        **ATTACHMENT_SCHEMA["properties"],
    },
}

ATTACHMENT_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"attachment": ATTACHMENT_DETAIL_SCHEMA},
}

ATTACHMENTS_SCHEMA: dict[str, Any] = {
    "type": "array",
    "items": copy.deepcopy(ATTACHMENT_SCHEMA),
}

ATTACHMENTS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "array",
    "items": copy.deepcopy(ATTACHMENT_DETAIL_SCHEMA),
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/attachments:get",
        "attachmets:get",
        "project_id/attachments/detail:get",
        "attachments/detail:get",
    ]:
        for pname in [
            "all_tenants",
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
    if name == "AttachmentsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**ATTACHMENTS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "AttachmentsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**ATTACHMENTS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "AttachmentShowResponse",
        "AttachmentsCreateResponse",
        "AttachmentUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**ATTACHMENT_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
