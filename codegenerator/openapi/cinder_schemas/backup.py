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

BACKUP_LIST_PARAMETERS: dict[str, Any] = {
    "backup_all_tenants": {
        "in": "query",
        "name": "all_tenants",
        "description": "Shows details for all project. Admin only.",
        "schema": {"type": "boolean"},
    },
    "backup_with_count": {
        "in": "query",
        "name": "with_count",
        "description": "Whether to show count in API response or not, default is False.",
        "schema": {"type": "boolean"},
        "x-openstack": {"min-ver": "3.45"},
    },
    "backup_sort": {
        "in": "query",
        "name": "sort",
        "description": "Comma-separated list of sort keys and optional sort directions in the form of < key > [: < direction > ]. A valid direction is asc (ascending) or desc (descending).",
        "schema": {"type": "string"},
    },
    "backup_sort_key": {
        "in": "query",
        "name": "sort_key",
        "description": "Sorts by an attribute. A valid value is name, status, container_format, disk_format, size, id, created_at, or updated_at. Default is created_at. The API uses the natural sorting direction of the sort_key attribute value. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "backup_sort_dir": {
        "in": "query",
        "name": "sort_dir",
        "description": "Sorts by one or more sets of attribute and sort direction combinations. If you omit the sort direction in a set, default is desc. Deprecated in favour of the combined sort parameter.",
        "schema": {"type": "string"},
    },
    "backup_limit": {
        "in": "query",
        "name": "limit",
        "description": "Requests a page size of items. Returns a number of items up to a limit value. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "integer"},
    },
    "backup_marker": {
        "in": "query",
        "name": "marker",
        "description": "The ID of the last-seen item. Use the limit parameter to make an initial limited request and use the ID of the last-seen item from the response as the marker parameter value in a subsequent limited request.",
        "schema": {"type": "string"},
    },
    "backup_offset": {
        "in": "query",
        "name": "offset",
        "description": "Used in conjunction with limit to return a slice of items. offset is where to start in the list.",
        "schema": {"type": "integer"},
    },
}

BACKUP_SHORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A backup object.",
    "properties": {
        "name": {
            "type": ["string", "null"],
            "description": "The backup name.",
        },
        "links": {
            "description": "The backup links.",
            **copy.deepcopy(common.LINKS_SCHEMA),
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the backup.",
        },
    },
}

BACKUP_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A backup object.",
    "properties": {
        "availability_zone": {
            "type": "string",
            "description": "The name of the availability zone.",
        },
        "container": {
            "type": ["string", "null"],
            "description": "The container name or null.",
        },
        "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was created. The date and time stamp format is ISO 8601",
        },
        "data_timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "The time when the data on the volume was first saved. If it is a backup from volume, it will be the same as created_at for a backup. If it is a backup from a snapshot, it will be the same as created_at for the snapshot.",
        },
        "description": {
            "type": ["string", "null"],
            "description": "The backup description or null.",
        },
        "fail_reason": {
            "type": ["string", "null"],
            "description": "If the backup failed, the reason for the failure. Otherwise, null.",
        },
        "has_dependent_backups": {
            "type": "boolean",
            "description": "If this value is true, there are other backups depending on this backup.",
        },
        "id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the backup.",
        },
        "is_incremental": {
            "type": "boolean",
            "description": "Indicates whether the backup mode is incremental. If this value is true, the backup mode is incremental. If this value is false, the backup mode is full.",
        },
        "links": {
            "description": "The backup links.",
            **copy.deepcopy(common.LINKS_SCHEMA),
        },
        "metadata": copy.deepcopy(common.METADATA_SCHEMA),
        "name": {
            "type": ["string", "null"],
            "description": "The backup name.",
        },
        "object_count": {
            "type": "integer",
            "description": "The number of objects in the backup.",
        },
        "size": {
            "type": "integer",
            "format": "int64",
            "description": "The size of the volume, in gibibytes (GiB).",
        },
        "snapshot_id": {
            "type": ["string", "null"],
            "format": "uuid",
            "description": "The UUID of the source volume snapshot.",
        },
        "status": {
            "type": "string",
            "description": "The backup status. Refer to Backup statuses table for the possible status value.",
        },
        "updated_at": {
            "type": "string",
            "format": "date-time",
            "description": "The date and time when the resource was updated. The date and time stamp format is ISO 8601",
        },
        "volume_id": {
            "type": "string",
            "format": "uuid",
            "description": "The UUID of the volume.",
        },
    },
}

BACKUPS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of backup objects.",
    "properties": {
        "backups": {
            "type": "array",
            "items": copy.deepcopy(BACKUP_SHORT_SCHEMA),
            "description": "A list of backup objects.",
        },
    },
}

BACKUPS_DETAIL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "A container with list of backup objects.",
    "properties": {
        "backups": {
            "type": "array",
            "items": copy.deepcopy(BACKUP_SCHEMA),
            "description": "A list of backup objects.",
        },
    },
}

BACKUP_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"backup": BACKUP_SCHEMA},
}

BACKUP_SHORT_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"backup": BACKUP_SHORT_SCHEMA},
}

BACKUP_RESTORE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "restore": {
            "type": "object",
            "properties": {
                "backup_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "The UUID for a backup.",
                },
                "volume_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "The UUID of the volume.",
                },
                "backup_name": {
                    "type": "string",
                    "description": "The volume name.",
                },
            },
        }
    },
}

BACKUP_RECORD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "backup-record": {
            "type": "object",
            "description": "An object recording volume backup metadata, including backup_service and backup_url.",
            "properties": {
                "backup_service": {
                    "type": "string",
                    "description": "The service used to perform the backup.",
                },
                "backup_url": {
                    "type": "string",
                    "format": "uri",
                    "description": "An identifier string to locate the backup.",
                },
            },
        }
    },
}


def _post_process_operation_hook(
    openapi_spec, operation_spec, path: str | None = None
):
    """Hook to allow service specific generator to modify details"""
    operationId = operation_spec.operationId
    if operationId in [
        "project_id/backups:get",
        "backups:get",
        "project_id/backups/detail:get",
        "backups/detail:get",
    ]:
        for key, val in BACKUP_LIST_PARAMETERS.items():
            openapi_spec.components.parameters.setdefault(
                key, ParameterSchema(**val)
            )
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
    if name == "BackupsDetailResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**BACKUPS_DETAIL_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "BackupsListResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**BACKUPS_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "BackupsCreateResponse",
        "BackupShowResponse",
        "BackupUpdateResponse",
    ]:
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**BACKUP_CONTAINER_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name == "BackupsImport_RecordResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**BACKUP_SHORT_CONTAINER_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name == "BackupsRestoreResponse":
        openapi_spec.components.schemas.setdefault(
            name,
            TypeSchema(**BACKUP_RESTORE_RESPONSE_SCHEMA),
        )
        ref = f"#/components/schemas/{name}"
    elif name == "BackupsExport_RecordResponse":
        openapi_spec.components.schemas.setdefault(
            name, TypeSchema(**BACKUP_RECORD_SCHEMA)
        )
        ref = f"#/components/schemas/{name}"
    elif name in [
        "BackupsActionOs-Reset_StatusResponse",
        "BackupsActionOs-Force_DeleteResponse",
    ]:
        return (None, None, True)
    else:
        return (None, None, False)

    return (ref, mime_type, True)
