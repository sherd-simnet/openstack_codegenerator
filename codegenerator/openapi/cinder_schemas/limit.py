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

LIMITS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "limits": {
            "type": "object",
            "properties": {
                "rate": {"type": "array"},
                "absolute": {
                    "type": "object",
                    "properties": {
                        "totalSnapshotsUsed": {
                            "type": "integer",
                            "description": "The total number of snapshots used.",
                        },
                        "maxTotalBackups": {
                            "type": "integer",
                            "description": "The maximum number of backups.",
                        },
                        "maxTotalVolumeGigabytes": {
                            "type": "integer",
                            "type": "int64",
                            "description": "The maximum total amount of volumes, in gibibytes (GiB).",
                        },
                        "maxTotalSnapshots": {
                            "type": "integer",
                            "description": "The maximum number of snapshots.",
                        },
                        "maxTotalBackupGigabytes": {
                            "type": "integer",
                            "type": "int64",
                            "description": "The maximum total amount of backups, in gibibytes (GiB).",
                        },
                        "totalBackupGigabytesUsed": {
                            "type": "integer",
                            "format": "int64",
                            "description": "The total number of backups gibibytes (GiB) used.",
                        },
                        "maxTotalVolumes": {
                            "type": "integer",
                            "description": "The maximum number of volumes.",
                        },
                        "totalVolumesUsed": {
                            "type": "integer",
                            "description": "The total number of volumes used.",
                        },
                        "totalBackupsUsed": {
                            "type": "integer",
                            "description": "The total number of backups used.",
                        },
                        "totalGigabytesUsed": {
                            "type": "integer",
                            "format": "int64",
                            "description": "The total number of gibibytes (GiB) used.",
                        },
                    },
                    "additionalProperties": False,
                    "required": [
                        "totalSnapshotsUsed",
                        "maxTotalBackups",
                        "maxTotalVolumeGigabytes",
                        "maxTotalSnapshots",
                        "maxTotalBackupGigabytes",
                        "totalBackupGigabytesUsed",
                        "maxTotalVolumes",
                        "totalVolumesUsed",
                        "totalBackupsUsed",
                        "totalGigabytesUsed",
                    ],
                },
            },
            "additionalProperties": False,
            "required": ["rate", "absolute"],
        }
    },
}


def _get_schema_ref(
    openapi_spec,
    name,
    description=None,
    schema_def=None,
    action_name=None,
) -> tuple[str | None, str | None, bool]:
    mime_type: str = "application/json"
    ref: str
    if name == "LimitsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**LIMITS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    else:
        return (None, None, False)

    return (ref, mime_type, True)
