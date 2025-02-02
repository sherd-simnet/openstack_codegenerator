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


RESOURCE_FILTERS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "resource_filters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "array",
                        "description": "The resource filter array",
                        "items": {"type": "string"},
                    },
                    "resource": {
                        "type": "string",
                        "description": "Resource which the filters will be applied to.",
                    },
                },
            },
        }
    },
}


def _get_schema_ref(
    openapi_spec, name, description=None, schema_def=None, action_name=None
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "Resource_FiltersListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**RESOURCE_FILTERS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
