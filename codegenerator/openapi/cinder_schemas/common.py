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

from cinder.api.schemas import admin_actions
from cinder.api.validation import parameter_types

# NOTE(gtema): This is a temporary location for schemas not currently defined
# in Cinder. Once everything is stabilized those must be moved directly to Cinder

OPENAPI_TAGS: dict[str, str] = {
    "attachments": """Lists all, lists all with details, shows details for, creates, and deletes attachment.

**Note**: Everything except for Complete attachment is new as of the 3.27 microversion. Complete attachment is new as of the 3.44 microversion.

When you create, list, update, or delete attachment, the possible status values are:

- attached: A volume is attached for the attachment.
- attaching: A volume is attaching for the attachment.
- detached: A volume is detached for the attachment.
- reserved: A volume is reserved for the attachment.
- error_attaching: A volume is error attaching for the attachment.
- error_detaching: A volume is error detaching for the attachment.
- deleted: The attachment is deleted.
    """,
    "backups": """A backup is a full copy of a volume stored in an external service.
The service can be configured. The only supported service is Object Storage. A backup can subsequently be restored from the external service to either the same volume that the backup was originally taken from or to a new volume.

When you create, list, or delete backups, these status values are possible:
- creating: The backup is being created.
- available: The backup is ready to restore to a volume.
- deleting: The backup is being deleted.
- error: A backup error occurred.
- restoring: The backup is being restored to a volume.
- error_deleting: An error occurred while deleting the backup.

If an error occurs, you can find more information about the error in the fail_reason field for the backup.
    """,
    "capabilities": "Shows capabilities for a storage back end.",
    "cgsnapshots": "Lists all, lists all with details, shows details for, creates, and deletes consistency group snapshots.",
    "clusters": """Administrator only. Lists all Cinder clusters, show cluster detail, enable or disable a cluster.

Each cinder service runs on a host computer (possibly multiple services on the same host; it depends how you decide to deploy cinder). In order to support High Availibility scenarios, services can be grouped into clusters where the same type of service (for example, cinder-volume) can run on different hosts so that if one host goes down the service is still available on a different host. Since there's no point having these services sitting around doing nothing while waiting for some other host to go down (which is also known as Active/Passive mode), grouping services into clusters also allows cinder to support Active/Active mode in which all services in a cluster are doing work all the time.

**Note**: Currently the only service that can be grouped into clusters is cinder-volume.

Clusters are determined by the deployment configuration; that's why there is no `create-cluster` API call listed below. Once your services are up and running, however, you can use the following API requests to get information about your clusters and to update their status.
    """,
    "consistencygroups": """Consistency groups enable you to create snapshots at the exact same point in time from multiple volumes. For example, a database might place its tables, logs, and configuration on separate volumes. To restore this database from a previous point in time, it makes sense to restore the logs, tables, and configuration together from the exact same point in time.

Use the policy configuration file to grant permissions for these actions to limit roles.
    """,
    "default-types": """Manage a default volume type for individual projects.

By default, a volume-create request that does not specify a volume-type will assign the configured system default volume type to the volume. You can override this behavior on a per-project basis by setting a different default volume type for any project.

Available in microversion 3.62 or higher.

**Note:** The default policy for list API is system admin so you would require a system scoped token to access it. To get a system scoped token, you need to run the following command:

openstack –os-system-scope all –os-project-name=’’ token issue
    """,
    "group_snapshots": """Lists all, lists all with details, shows details for, creates, and deletes group snapshots.
    """,
    "group_types": "To create a generic volume group, you must specify a group type.",
    "groups": """Generic volume groups enable you to create a group of volumes and manage them together.

How is generic volume groups different from consistency groups? Currently consistency groups in cinder only support consistent group snapshot. It cannot be extended easily to serve other purposes. A project may want to put volumes used in the same application together in a group so that it is easier to manage them together, and this group of volumes may or may not support consistent group snapshot. Generic volume group is introduced to solve this problem. By decoupling the tight relationship between the group construct and the consistency concept, generic volume groups can be extended to support other features in the future.
    """,
    "limits": "Shows absolute limits for a project.\n\nAn absolute limit value of -1 indicates that the absolute limit for the item is infinite.",
    "manageable_snapshots": "Creates or lists snapshots by using existing storage instead of allocating new storage.",
    "manageable_volumes": "Creates or lists volumes by using existing storage instead of allocating new storage.",
    "messages": """Lists all, shows, and deletes messages. These are error messages generated by failed operations as a way to find out what happened when an asynchronous operation failed.
    """,
    "os-hosts": "Administrators only, depending on policy settings.\n\nLists, shows hosts.",
    "os-quota-class-sets": "Administrators only, depending on policy settings.\n\nShows and updates quota classes for a project.",
    "os-quota-sets": "Administrators only, depending on policy settings.\n\nShows and updates, and deletes quotas for a project.",
    "os-services": "Administrator only. Lists all Cinder services, enables or disables a Cinder service, freeze or thaw the specified cinder-volume host, failover a replicating cinder-volume host.",
    "os-volume-transfer": "Transfers a volume from one user to another user.",
    "qos-specs": """Administrators only, depending on policy settings.

Creates, lists, shows details for, associates, disassociates, sets keys, unsets keys, and deletes quality of service (QoS) specifications.
    """,
    "resource_filters": "Lists all resource filters, available since microversion 3.33.",
    "scheduler-stats": "Administrator only. Lists all back-end storage pools that are known to the scheduler service.",
    "snapshots": """A snapshot is a point-in-time copy of the data that a volume contains.

When you create, list, or delete snapshots, these status values are possible:

- creating: The snapshot is being created.
- available: The snapshot is ready to use.
- backing-up: The snapshot is being backed up.
- deleting: The snapshot is being deleted.
- error: A snapshot creation error occurred.
- deleted: The snapshot has been deleted.
- unmanaging: The snapshot is being unmanaged.
- restoring: The snapshot is being restored to a volume.
- error_deleting: A snapshot deletion error occurred.
    """,
    "types": """To create an environment with multiple-storage back ends, you must specify a volume type. The API spawns Block Storage volume back ends as children to cinder-volume, and keys them from a unique queue. The API names the back ends cinder-volume.HOST.BACKEND. For example, cinder-volume.ubuntu.lvmdriver. When you create a volume, the scheduler chooses an appropriate back end for the volume type to handle the request.
    """,
    "volume-transfers": "Transfers a volume from one user to another user. This is the new transfer APIs with microversion 3.55.",
    "volumes": """A volume is a detachable block storage device similar to a USB hard drive. You can attach a volume to an instance, and if the volume is of an appropriate volume type, a volume can be attached to multiple instances.

The snapshot_id and source_volid parameters specify the ID of the snapshot or volume from which this volume originates. If the volume was not created from a snapshot or source volume, these values are null.

When you create, list, update, or delete volumes, the possible status values are:

- creating: The volume is being created.
- available: The volume is ready to attach to an instance.
- reserved: The volume is reserved for attaching or shelved.
- attaching: The volume is attaching to an instance.
- detaching: The volume is detaching from an instance.
- in-use: The volume is attached to an instance.
- maintenance: The volume is locked and being migrated.
- deleting: The volume is being deleted.
- awaiting-transfer: The volume is awaiting for transfer.
- error: A volume creation error occurred.
- error_deleting: A volume deletion error occurred.
- backing-up: The volume is being backed up.
- restoring-backup: A backup is being restored to the volume.
- error_backing-up: A backup error occurred.
- error_restoring: A backup restoration error occurred.
- error_extending: An error occurred while attempting to extend a volume.
- downloading: The volume is downloading an image.
- uploading: The volume is being uploaded to an image.
- retyping: The volume is changing type to another volume type.
- extending: The volume is being extended.
    """,
}


LINK_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Links to the resources in question. See [API Guide / Links and References](https://docs.openstack.org/api-guide/compute/links_and_references.html) for more info.",
    "properties": {
        "href": {"type": "string", "format": "uri"},
        "rel": {"type": "string"},
    },
}

LINKS_SCHEMA: dict[str, Any] = {
    "type": "array",
    "description": "Links to the resources in question. See [API Guide / Links and References](https://docs.openstack.org/api-guide/compute/links_and_references.html) for more info.",
    "items": copy.deepcopy(LINK_SCHEMA),
}

METADATA_SCHEMA: dict[str, Any] = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9-_:. /]{1,255}$": {"type": "string", "maxLength": 255},
    },
    "additionalProperties": False,
    "description": "A metadata object. Contains one or more metadata key and value pairs that are associated with the resource.",
}

METADATA_CONTAINER_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Metadata key and value pairs. The maximum size for each metadata key and value pair is 255 bytes.",
    "properties": {"metadata": METADATA_SCHEMA},
}

METADATA_ITEM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Metadata key and value pairs. The maximum size for each metadata key and value pair is 255 bytes.",
    "properties": {"meta": {"maxProperties": 1, **METADATA_SCHEMA}},
}

AVAILABILITY_ZONES_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "availabilityZoneInfo": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "zoneName": {
                        "type": "string",
                        "description": "The availability zone name.",
                    },
                    "zoneState": {
                        "type": "object",
                        "properties": {"available": {"type": "boolean"}},
                    },
                },
            },
        }
    },
}
