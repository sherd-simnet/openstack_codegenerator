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

from codegenerator.common.schema import TypeSchema

EXTENSION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "updated": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was updated.",
        },
        "description": {
            "type": "string",
            "description": "The extension description.",
        },
        "links": {"type": "array", "description": ""},
        "alias": {
            "type": "string",
            "description": "The alias for the extension. For example, “FOXNSOX”, “os- availability-zone”, “os-extended-quotas”, “os- share-unmanage” or “os-used-limits.”",
        },
        "name": {"type": "string", "description": "The name of the object."},
    },
    "additionalProperties": False,
    "required": ["updated", "links", "alias", "name", "description"],
}

EXTENSIONS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of extension objects.",
    "properties": {
        "extensions": {
            "type": "array",
            "items": copy.deepcopy(EXTENSION_SCHEMA),
        },
    },
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/extensions:post",
        "project_id/extensions/id:get",
        "project_id/extensions/id:delete",
        "extensions:post",
        "extensions/id:get",
        "extensions/id:delete",
    ]:
        operation_spec = None


def _get_schema_ref(
    openapi_spec,
    name,
    description=None,
    schema_def=None,
    action_name=None,
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "ExtensionsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**EXTENSIONS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
