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
from pathlib import Path
import logging
import re

import jsonref
from ruamel.yaml import YAML

from codegenerator.base import BaseGenerator
from codegenerator import common
from codegenerator.common.schema import SpecSchema
from codegenerator.types import Metadata
from codegenerator.types import OperationModel
from codegenerator.types import OperationTargetParams
from codegenerator.types import ResourceModel

OPERATION_ID_BLACKLIST: set[str] = {
    # # BlockStorage
    # ## Host put has no schema
    "project_id/os-hosts:put",
    "os-hosts:put",
    "project_id/os-hosts/id:put",
    "os-hosts/id:put",
}


class MetadataGenerator(BaseGenerator):
    """Generate metadata from OpenAPI spec"""

    def load_openapi(self, path):
        """Load existing OpenAPI spec from the file"""
        if not path.exists():
            return
        yaml = YAML(typ="safe")
        with open(path) as fp:
            spec = jsonref.replace_refs(yaml.load(fp))

        return SpecSchema(**spec)

    def generate(
        self, res, target_dir, openapi_spec=None, operation_id=None, args=None
    ):
        """Generate Json Schema definition file for Resource"""
        logging.debug("Generating OpenAPI schema data")
        # We do not import generators since due to the use of Singletons in the
        # code importing glance, nova, cinder at the same time crashes
        # dramatically
        spec_path = Path(args.openapi_yaml_spec)
        metadata_path = Path(target_dir, args.service_type + "_metadata.yaml")

        schema = self.load_openapi(spec_path)
        openapi_spec = common.get_openapi_spec(spec_path)
        metadata = Metadata(resources={})
        api_ver = "v" + schema.info["version"].split(".")[0]
        for path, spec in schema.paths.items():
            path_elements: list[str] = path.split("/")
            resource_name = "/".join(
                list(common.get_resource_names_from_url(path))
            )
            if args.service_type == "object-store":
                if path == "/v1/{account}":
                    resource_name = "account"
                elif path == "/v1/{account}/{container}":
                    resource_name = "container"
                if path == "/v1/{account}/{object}":
                    resource_name = "object"

            if args.service_type == "compute" and resource_name in [
                "agent",
                "baremetal_node",
                "cell",
                "cell/capacity",
                "cell/info",
                "cell/sync_instance",
                "certificate",
                "cloudpipe",
                "fping",
                "fixed_ip",
                "floating_ip_dns",
                "floating_ip_dns/entry",
                "floating_ip_pool",
                "floating_ip_bulk",
                "host",
                "host/reboot",
                "host/shutdown",
                "host/startup",
                "image",
                "image/metadata",
                "network",
                "security_group_default_rule",
                "security_group_rule",
                "security_group",
                "server/console",
                "server/virtual_interface",
                "snapshot",
                "tenant_network",
                "volume",
                "volumes_boot",
            ]:
                # We do not need to produce anything for deprecated APIs
                continue
            resource_model = metadata.resources.setdefault(
                f"{args.service_type}.{resource_name}",
                ResourceModel(
                    api_version=api_ver,
                    spec_file=spec_path.as_posix(),
                    operations={},
                ),
            )
            for method in [
                "head",
                "get",
                "put",
                "post",
                "delete",
                "options",
                "patch",
            ]:
                operation = getattr(spec, method, None)
                if operation:
                    if not operation.operationId:
                        # Every operation must have operationId
                        continue
                    if operation.operationId in OPERATION_ID_BLACKLIST:
                        # For blacklisted operationIds were are not producing anything
                        continue

                    op_model = OperationModel(
                        operation_id=operation.operationId, targets={}
                    )
                    operation_key: str | None = None

                    response_schema: dict | None = None
                    for code, rsp in operation.responses.items():
                        if code.startswith("2"):
                            response_schema = (
                                rsp.get("content", {})
                                .get("application/json", {})
                                .get("schema", {})
                            )
                            break
                    if path.endswith("}"):
                        if method == "get":
                            operation_key = "show"
                        elif method == "head":
                            operation_key = "check"
                        elif method == "put":
                            operation_key = "update"
                        elif method == "patch":
                            if "application/json" in operation.requestBody.get(
                                "content", {}
                            ):
                                operation_key = "update"
                            else:
                                operation_key = "patch"
                        elif method == "post":
                            operation_key = "create"
                        elif method == "delete":
                            operation_key = "delete"
                    elif (
                        path.endswith("/detail")
                        and resource_name != "quota_set"
                    ):
                        if method == "get":
                            operation_key = "list_detailed"
                    # elif path.endswith("/default"):
                    #     operation_key = "default"
                    elif path == "/v2/images/{image_id}/file":
                        if method == "put":
                            operation_key = "upload"
                        elif method == "get":
                            operation_key = "download"
                        else:
                            raise NotImplementedError
                    elif path == "/v3/users/{user_id}/password":
                        if method == "post":
                            operation_key = "update"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "flavor/flavor_access"
                        and method == "get"
                    ):
                        operation_key = "list"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "aggregate/image"
                        and method == "post"
                    ):
                        operation_key = "action"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "server/security_group"
                        and method == "get"
                    ):
                        operation_key = "list"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "server/topology"
                        and method == "get"
                    ):
                        operation_key = "list"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "quota_set"
                        and path.endswith("defaults")
                    ):
                        operation_key = "defaults"
                    elif (
                        args.service_type == "compute"
                        and resource_name == "quota_set"
                        and path.endswith("detail")
                    ):
                        # normalize "details" name
                        operation_key = "details"
                    elif (
                        args.service_type == "load-balancer"
                        and len(path_elements) > 1
                        and path_elements[-1]
                        in ["stats", "status", "failover", "config"]
                    ):
                        operation_key = path_elements[-1]

                    elif response_schema and (
                        method == "get"
                        and (
                            response_schema.get("type", "") == "array"
                            or (
                                response_schema.get("type", "") == "object"
                                and "properties" in response_schema
                                and len(path_elements) > 1
                                and path_elements[-1]
                                in response_schema.get("properties", {})
                            )
                        )
                    ):
                        # Response looks clearly like a list
                        operation_key = "list"
                    elif path.endswith("/action"):
                        # Action
                        operation_key = "action"
                    elif args.service_type == "image" and path.endswith(
                        "/actions/deactivate"
                    ):
                        operation_key = "deactivate"
                    elif args.service_type == "image" and path.endswith(
                        "/actions/reactivate"
                    ):
                        operation_key = "reactivate"
                    elif (
                        args.service_type == "block-storage"
                        and "volume-transfer" in path
                        and path.endswith("/accept")
                    ):
                        operation_key = "accept"
                    elif (
                        args.service_type == "block-storage"
                        and "qos-specs" in path
                        and path_elements[-1]
                        in [
                            "associate",
                            "disassociate",
                            "disassociate_all",
                            "delete_keys",
                        ]
                    ):
                        operation_key = path_elements[-1]
                    elif (
                        args.service_type == "network"
                        and "quota" in path
                        and path.endswith("/default")
                    ):
                        # normalize "defaults" name
                        operation_key = "defaults"
                    elif (
                        args.service_type == "network"
                        and "quota" in path
                        and path.endswith("/details")
                    ):
                        operation_key = "details"
                    elif (
                        len(
                            [
                                x
                                for x in schema.paths.keys()
                                if x.startswith(path + "/{")
                            ]
                        )
                        > 0
                    ):
                        # if we are at i.e. /v2/servers and there is
                        # /v2/servers/{ most likely we are at the collection
                        # level
                        if method == "get":
                            operation_key = "list"
                        elif method == "head":
                            operation_key = "check"
                        elif method == "patch":
                            if "application/json" in operation.requestBody.get(
                                "content", {}
                            ):
                                operation_key = "update"
                            else:
                                operation_key = "patch"
                        elif method == "post":
                            operation_key = "create"
                        elif method == "put":
                            operation_key = "replace"
                        elif method == "delete":
                            operation_key = "delete_all"
                    elif method == "head":
                        operation_key = "check"
                    elif method == "get":
                        operation_key = "get"
                    elif method == "post":
                        operation_key = "create"
                    elif method == "put":
                        operation_key = path.split("/")[-1]
                    elif method == "patch":
                        if "application/json" in operation.requestBody.get(
                            "content", {}
                        ):
                            operation_key = "update"
                        else:
                            operation_key = "patch"
                    elif method == "delete":
                        operation_key = "delete"
                    if not operation_key:
                        logging.warn(
                            f"Cannot identify op name for {path}:{method}"
                        )

                    # Next hacks
                    if args.service_type == "identity" and resource_name in [
                        "OS_FEDERATION/identity_provider",
                        "OS_FEDERATION/identity_provider/protocol",
                        "OS_FEDERATION/mapping",
                        "OS_FEDERATION/service_provider",
                    ]:
                        if method == "put":
                            operation_key = "create"
                        elif method == "patch":
                            operation_key = "update"
                    if (
                        args.service_type == "identity"
                        and resource_name
                        in [
                            "domain/config",
                            "domain/config/group",
                            "domain/config/group/option",
                        ]
                        and path.endswith("/default")
                        and method == "get"
                    ):
                        operation_key = "default"

                    if (
                        args.service_type == "identity"
                        and resource_name
                        in [
                            "domain/config",
                            "domain/config/group",
                            "domain/config/group/option",
                        ]
                        and path.endswith("/default")
                        and method == "head"
                    ):
                        # No need in HEAD defaults
                        continue
                    if args.service_type == "object-store":
                        if resource_name == "object":
                            mapping_obj: dict[str, str] = {
                                "head": "head",
                                "get": "get",
                                "delete": "delete",
                                "put": "put",
                                "post": "update",
                            }
                            operation_key = mapping_obj[method]
                        elif resource_name == "container":
                            mapping_cont: dict[str, str] = {
                                "head": "head",
                                "get": "get",
                                "delete": "delete",
                                "put": "create",
                                "post": "update",
                            }
                            operation_key = mapping_cont[method]
                        elif resource_name == "account":
                            mapping_account: dict[str, str] = {
                                "head": "head",
                                "get": "get",
                                "delete": "delete",
                                "put": "create",
                                "post": "update",
                            }
                            operation_key = mapping_account[method]

                    if operation_key in resource_model:
                        raise RuntimeError("Operation name conflict")
                    else:
                        if operation_key == "action" and args.service_type in [
                            "compute",
                            "block-storage",
                        ]:
                            # For action we actually have multiple independent operations
                            try:
                                body_schema = operation.requestBody["content"][
                                    "application/json"
                                ]["schema"]
                                bodies = body_schema.get(
                                    "oneOf", [body_schema]
                                )
                                if len(bodies) > 1:
                                    discriminator = body_schema.get(
                                        "x-openstack", {}
                                    ).get("discriminator")
                                    if discriminator != "action":
                                        raise RuntimeError(
                                            f"Cannot generate metadata for {path} since request body is not having action discriminator"
                                        )
                                for body in bodies:
                                    action_name = body.get(
                                        "x-openstack", {}
                                    ).get("action-name")
                                    if not action_name:
                                        action_name = list(
                                            body["properties"].keys()
                                        )[0]
                                    # Hardcode fixes
                                    if (
                                        resource_name == "flavor"
                                        and action_name
                                        in ["update", "create", "delete"]
                                    ):
                                        # Flavor update/create/delete
                                        # operations are exposed ALSO as wsgi
                                        # actions. This is wrong and useless.
                                        logging.warn(
                                            "Skipping generating %s:%s action",
                                            resource_name,
                                            action_name,
                                        )
                                        continue

                                    operation_name = "-".join(
                                        x.lower()
                                        for x in re.split(
                                            common.SPLIT_NAME_RE, action_name
                                        )
                                    ).lower()
                                    rust_sdk_params = (
                                        get_rust_sdk_operation_args(
                                            "action",
                                            operation_name=action_name,
                                            module_name=get_module_name(
                                                action_name
                                            ),
                                        )
                                    )
                                    rust_cli_params = (
                                        get_rust_cli_operation_args(
                                            "action",
                                            operation_name=action_name,
                                            module_name=get_module_name(
                                                action_name
                                            ),
                                            resource_name=resource_name,
                                        )
                                    )

                                    op_model = OperationModel(
                                        operation_id=operation.operationId,
                                        targets={},
                                    )
                                    op_model.operation_type = "action"

                                    op_model.targets["rust-sdk"] = (
                                        rust_sdk_params
                                    )
                                    op_model.targets["rust-cli"] = (
                                        rust_cli_params
                                    )

                                    op_model = post_process_operation(
                                        args.service_type,
                                        resource_name,
                                        operation_name,
                                        op_model,
                                    )

                                    resource_model.operations[
                                        operation_name
                                    ] = op_model

                            except KeyError:
                                raise RuntimeError(
                                    f"Cannot get bodies for {path}"
                                )
                        else:
                            if not operation_key:
                                raise NotImplementedError
                            operation_type = get_operation_type_by_key(
                                operation_key
                            )
                            op_model.operation_type = operation_type
                            # NOTE: sdk gets operation_key and not operation_type
                            rust_sdk_params = get_rust_sdk_operation_args(
                                operation_key
                            )
                            rust_cli_params = get_rust_cli_operation_args(
                                operation_key, resource_name=resource_name
                            )

                            op_model.targets["rust-sdk"] = rust_sdk_params
                            if rust_cli_params and not (
                                args.service_type == "identity"
                                and operation_key == "check"
                            ):
                                op_model.targets["rust-cli"] = rust_cli_params

                            op_model = post_process_operation(
                                args.service_type,
                                resource_name,
                                operation_key,
                                op_model,
                            )

                            resource_model.operations[operation_key] = op_model
        for res_name, res_data in metadata.resources.items():
            # Sanitize produced metadata
            list_op = res_data.operations.get("list")
            list_detailed_op = res_data.operations.get("list_detailed")
            if list_op and list_detailed_op:
                # There are both plain list and list with details operation.
                # For the certain generator backend it makes no sense to have
                # then both so we should disable generation of certain backends
                # for the non detailed endpoint
                list_op.targets.pop("rust-cli")

            # Prepare `find` operation data
            if (list_op or list_detailed_op) and res_data.operations.get(
                "show"
            ):
                show_op = res_data.operations["show"]

                (path, _, spec) = common.find_openapi_operation(
                    openapi_spec, show_op.operation_id
                )
                mod_path = common.get_rust_sdk_mod_path(
                    args.service_type, res_data.api_version or "", path
                )
                response_schema = None
                for code, rspec in spec.get("responses", {}).items():
                    if not code.startswith("2"):
                        continue
                    content = rspec.get("content", {})
                    if "application/json" in content:
                        try:
                            (response_schema, _) = common.find_resource_schema(
                                content["application/json"].get("schema", {}),
                                None,
                            )
                        except Exception as ex:
                            logging.exception(
                                "Cannot process response of %s operation: %s",
                                show_op.operation_id,
                                ex,
                            )

                if not response_schema:
                    # Show does not have a suitable
                    # response. We can't have find
                    # for such
                    continue
                if "id" not in response_schema.get("properties", {}).keys():
                    # Resource has no ID in show method => find impossible
                    continue
                elif (
                    "name" not in response_schema.get("properties", {}).keys()
                    and res_name != "floatingip"
                ):
                    # Resource has no NAME => find useless
                    continue

                list_op_ = list_detailed_op or list_op
                if not list_op_:
                    continue
                (_, _, list_spec) = common.find_openapi_operation(
                    openapi_spec, list_op_.operation_id
                )
                name_field: str = "name"
                for fqan, alias in common.FQAN_ALIAS_MAP.items():
                    if fqan.startswith(res_name) and alias == "name":
                        name_field = fqan.split(".")[-1]
                name_filter_supported: bool = False
                if name_field in [
                    x.get("name")
                    for x in list(list_spec.get("parameters", []))
                ]:
                    name_filter_supported = True

                sdk_params = OperationTargetParams(
                    module_name="find",
                    name_field=name_field,
                    name_filter_supported=name_filter_supported,
                    sdk_mod_path="::".join(mod_path),
                    list_mod="list_detailed" if list_detailed_op else "list",
                )
                res_data.operations["find"] = OperationModel(
                    operation_id=list_op_.operation_id,
                    operation_type="find",
                    targets={"rust-sdk": sdk_params},
                )

                # Let other operations know of `find` presence
                for op_name, op_data in res_data.operations.items():
                    if op_name not in ["find", "list", "create"]:
                        for (
                            target_name,
                            target_params,
                        ) in op_data.targets.items():
                            if target_name in ["rust-cli"]:
                                target_params.find_implemented_by_sdk = True

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        metadata_path.parent.mkdir(exist_ok=True, parents=True)
        with open(metadata_path, "w") as fp:
            yaml.dump(
                metadata.model_dump(
                    exclude_none=True, exclude_defaults=True, by_alias=True
                ),
                fp,
            )


def get_operation_type_by_key(operation_key):
    if operation_key in ["list", "list_detailed"]:
        return "list"
    elif operation_key in ["get", "stats", "status"]:
        return "get"
    elif operation_key == "check":
        return "get"
    elif operation_key == "show":
        return "show"
    elif operation_key in ["update", "replace"]:
        return "set"
    elif operation_key in ["delete", "delete_all"]:
        return "delete"
    elif operation_key in ["create"]:
        return "create"
    elif operation_key == "patch":
        return "set"
    elif operation_key == "default":
        return "show"
    elif operation_key == "defaults":
        return "show"
    elif operation_key == "details":
        return "show"
    elif operation_key == "download":
        return "download"
    elif operation_key == "upload":
        return "upload"
    elif operation_key in ["associate", "disassociate", "disassociate_all"]:
        # Cinder XXXssociate are GET actions not accepting body - crazy
        return "get"
    else:
        return "action"


def get_rust_sdk_operation_args(
    operation_key: str,
    operation_name: str | None = None,
    module_name: str | None = None,
):
    """Construct proper Rust SDK parameters for operation by type"""
    sdk_params = OperationTargetParams()
    sdk_params.module_name = module_name
    if operation_key == "show":
        sdk_params.module_name = "get"
    elif operation_key == "list_detailed":
        sdk_params.module_name = "list_detailed"
    #    elif operation_key == "action" and not module_name:
    #        sdk_params.module_name = operation_name if operation_name else operation_key
    else:
        sdk_params.module_name = module_name or get_module_name(
            # get_operation_type_by_key(operation_key)
            operation_key
        )
    sdk_params.operation_name = operation_name

    return sdk_params


def get_rust_cli_operation_args(
    operation_key: str,
    operation_name: str | None = None,
    module_name: str | None = None,
    resource_name: str | None = None,
):
    """Construct proper Rust CLI parameters for operation by type"""
    # Get SDK params to connect things with each other
    # operation_type = get_operation_type_by_key(operation_key)
    sdk_params = get_rust_sdk_operation_args(
        operation_key, operation_name=operation_name, module_name=module_name
    )
    cli_params = OperationTargetParams()
    cli_params.sdk_mod_name = sdk_params.module_name
    cli_params.module_name = module_name or get_module_name(operation_key)
    cli_params.operation_name = operation_name
    if resource_name:
        op_name = cli_params.module_name
        if op_name.startswith("os_") or op_name.startswith("os-"):
            op_name = op_name[3:]
        op_name = op_name.replace("_", "-")

        cli_params.cli_full_command = (
            " ".join(x for x in resource_name.split("/")).replace("_", "-")
            + " "
            + op_name
        )

    return cli_params


def get_module_name(name):
    if name in ["list", "list_detailed"]:
        return "list"
    elif name == "get":
        return "get"
    elif name == "show":
        return "show"
    elif name == "check":
        return "head"
    elif name == "update":
        return "set"
    elif name == "replace":
        return "replace"
    elif name == "delete":
        return "delete"
    elif name == "delete_all":
        return "delete_all"
    elif name in ["create"]:
        return "create"
    elif name in ["default"]:
        return "default"
    return "_".join(x.lower() for x in re.split(common.SPLIT_NAME_RE, name))


def post_process_operation(
    service_type: str, resource_name: str, operation_name: str, operation
):
    if service_type == "compute":
        operation = post_process_compute_operation(
            resource_name, operation_name, operation
        )
    elif service_type == "identity":
        operation = post_process_identity_operation(
            resource_name, operation_name, operation
        )
    elif service_type == "image":
        operation = post_process_image_operation(
            resource_name, operation_name, operation
        )
    elif service_type in ["block-storage", "volume"]:
        operation = post_process_block_storage_operation(
            resource_name, operation_name, operation
        )
    elif service_type == "network":
        operation = post_process_network_operation(
            resource_name, operation_name, operation
        )
    elif service_type == "object-store":
        operation = post_process_object_store_operation(
            resource_name, operation_name, operation
        )
    return operation


def post_process_compute_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name == "aggregate":
        if operation_name in ["set-metadata", "add-host", "remove-host"]:
            operation.targets["rust-sdk"].response_key = "aggregate"
            operation.targets["rust-cli"].response_key = "aggregate"
    elif resource_name == "availability_zone":
        if operation_name == "get":
            operation.operation_type = "list"
            operation.targets["rust-sdk"].operation_name = "list"
            operation.targets["rust-sdk"].response_key = "availabilityZoneInfo"
            operation.targets["rust-sdk"].module_name = "list"
            operation.targets["rust-cli"].response_key = "availabilityZoneInfo"
            operation.targets["rust-cli"].module_name = "list"
            operation.targets["rust-cli"].sdk_mod_name = "list"
            operation.targets["rust-cli"].operation_name = "list"
            operation.targets["rust-sdk"].response_key = "availabilityZoneInfo"
            operation.targets[
                "rust-cli"
            ].cli_full_command = "availability-zone list"
        elif operation_name == "list_detailed":
            operation.operation_type = "list"
            operation.targets["rust-sdk"].operation_name = "list_detail"
            operation.targets["rust-sdk"].response_key = "availabilityZoneInfo"
            operation.targets["rust-sdk"].module_name = "list_detail"
            operation.targets["rust-cli"].response_key = "availabilityZoneInfo"
            operation.targets["rust-cli"].operation_name = "list"
            operation.targets["rust-cli"].module_name = "list_detail"
            operation.targets["rust-cli"].sdk_mod_name = "list_detail"
            operation.targets[
                "rust-cli"
            ].cli_full_command = "availability-zone list-detail"

    elif resource_name == "keypair":
        if operation_name == "list":
            operation.targets["rust-sdk"].response_list_item_key = "keypair"

    elif resource_name == "server":
        if "migrate-live" in operation_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("migrate-live", "live-migrate")
    elif resource_name == "server/instance_action":
        if operation_name == "list":
            operation.targets["rust-sdk"].response_key = "instanceActions"
            operation.targets["rust-cli"].response_key = "instanceActions"
        else:
            operation.targets["rust-sdk"].response_key = "instanceAction"
            operation.targets["rust-cli"].response_key = "instanceAction"
    elif resource_name == "server/topology":
        if operation_name == "list":
            operation.targets["rust-sdk"].response_key = "nodes"
            operation.targets["rust-cli"].response_key = "nodes"
    elif resource_name == "server/volume_attachment":
        if operation_name == "list":
            operation.targets["rust-sdk"].response_key = "volumeAttachments"
            operation.targets["rust-cli"].response_key = "volumeAttachments"
        elif operation_name in ["create", "show", "update"]:
            operation.targets["rust-sdk"].response_key = "volumeAttachment"
            operation.targets["rust-cli"].response_key = "volumeAttachment"
    elif resource_name == "server/server_password":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("server-password", "password")
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("get", "show")
    elif resource_name == "server/security_group":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("security-group list", "security-groups")
        if operation_name == "get":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("get", "show")

    elif resource_name == "flavor":
        if operation_name == "add-tenant-access":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("add-tenant-access", "access add")
        elif operation_name == "list-tenant-access":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("list-tenant-access", "access list")
        elif operation_name == "remove-tenant-access":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("remove-tenant-access", "access remove")

    if resource_name == "limit":
        # Limits API return object and not a list
        operation.targets["rust-cli"].operation_type = "show"
        operation.targets["rust-cli"].response_key = "limits"
        operation.targets["rust-sdk"].response_key = "limits"

    if "/tag" in resource_name:
        if operation_name == "update":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("set", "add")
        elif operation_name == "show":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("show", "check")

    if operation_name == "delete_all":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("delete-all", "purge")

    return operation


def post_process_identity_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name == "role/imply":
        if operation_name == "list":
            operation.targets["rust-cli"].response_key = "role_inference"
            operation.targets["rust-sdk"].response_key = "role_inference"
    if resource_name == "role_inference":
        if operation_name == "list":
            operation.targets["rust-cli"].response_key = "role_inferences"
            operation.targets["rust-sdk"].response_key = "role_inferences"

    if resource_name == "domain/config/group":
        operation.targets["rust-sdk"].response_key = "config"
        if "rust-cli" in operation.targets:
            operation.targets["rust-cli"].response_key = "config"
    elif resource_name == "domain/config/group/option":
        operation.targets["rust-sdk"].response_key = "config"
        if "rust-cli" in operation.targets:
            operation.targets["rust-cli"].response_key = "config"

    if "rust-cli" in operation.targets:
        if "OS_FEDERATION" in resource_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("OS-FEDERATION", "federation")
        elif resource_name == "user/project":
            operation.targets["rust-cli"].cli_full_command = "user projects"
        elif resource_name == "user/group":
            operation.targets["rust-cli"].cli_full_command = "user groups"
        elif resource_name == "user/access_rule":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("user access-rule", "access-rule")
        elif resource_name == "user/application_credential":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace(
                "user application-credential", "application-credential"
            )

    if "/tag" in resource_name:
        if operation_name == "update":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("set", "add")
        elif operation_name == "show":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("show", "check")

    if operation_name == "delete_all":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("delete-all", "purge")

    return operation


def post_process_image_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name.startswith("schema"):
        # Image schemas are a JSON operation
        operation.targets["rust-cli"].operation_type = "json"
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("get", "show")
    elif resource_name == "metadef/namespace" and operation_name != "list":
        operation.targets["rust-sdk"].response_key = "null"
        operation.targets["rust-cli"].response_key = "null"
    elif (
        resource_name == "metadef/namespace/property"
        and operation_name == "list"
    ):
        operation.targets["rust-cli"].operation_type = "list_from_struct"
        operation.targets["rust-cli"].response_key = "properties"
        operation.targets["rust-sdk"].response_key = "properties"
    elif resource_name == "metadef/namespace/resource_type":
        operation.targets[
            "rust-cli"
        ].response_key = "resource_type_associations"
        operation.targets[
            "rust-sdk"
        ].response_key = "resource_type_associations"
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace(
            "resource-type", "resource-type-association"
        )
    elif resource_name == "image":
        if operation_name == "patch":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("patch", "set")
    elif resource_name == "image/file":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("file ", "")

    if "/tag" in resource_name:
        if operation_name == "update":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("set", "add")
        elif operation_name == "show":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("show", "check")

    if operation_name == "delete_all":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("delete-all", "purge")

    return operation


def post_process_block_storage_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name == "type":
        if operation_name == "list":
            operation.targets["rust-cli"].response_key = "volume_types"
            operation.targets["rust-sdk"].response_key = "volume_types"
        elif operation_name in ["create", "show", "update"]:
            operation.targets["rust-cli"].response_key = "volume_type"
            operation.targets["rust-sdk"].response_key = "volume_type"
    elif resource_name == "type/volume_type_access":
        operation.targets["rust-cli"].response_key = "volume_type_access"
        operation.targets["rust-sdk"].response_key = "volume_type_access"

    if "/tag" in resource_name:
        if operation_name == "update":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("set", "add")
        elif operation_name == "show":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("show", "check")

    if resource_name == "snapshot":
        if "update-snapshot-status" in operation_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace(
                "update-snapshot-status", "update-status"
            )

    if resource_name in ["os_volume_transfer", "volume_transfer"]:
        if operation_name in ["list", "list_detailed"]:
            operation.targets["rust-cli"].response_key = "transfers"
            operation.targets["rust-sdk"].response_key = "transfers"
        elif operation_name in ["accept", "create", "show"]:
            operation.targets["rust-cli"].response_key = "transfer"

    if resource_name == "availability_zone":
        if operation_name == "get":
            operation.operation_type = "list"
            operation.targets["rust-sdk"].operation_name = "list"
            operation.targets["rust-sdk"].response_key = "availabilityZoneInfo"
            operation.targets["rust-sdk"].module_name = "list"
            operation.targets["rust-cli"].response_key = "availabilityZoneInfo"
            operation.targets["rust-cli"].module_name = "list"
            operation.targets["rust-cli"].sdk_mod_name = "list"
            operation.targets["rust-cli"].operation_name = "list"
            operation.targets["rust-sdk"].response_key = "availabilityZoneInfo"
            operation.targets[
                "rust-cli"
            ].cli_full_command = "availability-zone list"
    if resource_name == "qos_spec/association":
        operation.operation_type = "list"
        operation.targets["rust-sdk"].operation_name = "list"
        operation.targets["rust-sdk"].module_name = "list"
        operation.targets["rust-cli"].operation_name = "list"
        operation.targets["rust-cli"].module_name = "list"
        operation.targets["rust-cli"].sdk_mod_name = "list"
        operation.targets["rust-sdk"].response_key = "qos_associations"
        operation.targets["rust-cli"].response_key = "qos_associations"
        operation.targets[
            "rust-cli"
        ].cli_full_command = "qos-spec association list"

    if resource_name == "limit" and operation_name == "list":
        # Limits API return object and not a list
        operation.targets["rust-cli"].operation_type = "show"

    if operation_name == "delete_all":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("delete-all", "purge")

    return operation


def post_process_network_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name.startswith("floatingip"):
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("floatingip", "floating-ip")

    if resource_name == "router":
        if "external_gateways" in operation_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("external-gateways", "external-gateway")
        elif "extraroutes" in operation_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("extraroutes", "extraroute")

    if resource_name == "address_group":
        if "addresses" in operation_name:
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("addresses", "address")

    if "/tag" in resource_name:
        if operation_name == "update":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("set", "add")
        elif operation_name == "show":
            operation.targets["rust-cli"].cli_full_command = operation.targets[
                "rust-cli"
            ].cli_full_command.replace("show", "check")

    if operation_name == "delete_all":
        operation.targets["rust-cli"].cli_full_command = operation.targets[
            "rust-cli"
        ].cli_full_command.replace("delete-all", "purge")

    return operation


def post_process_object_store_operation(
    resource_name: str, operation_name: str, operation
):
    if resource_name == "account":
        if operation_name == "get":
            operation.targets["rust-cli"].cli_full_command = "container list"
        elif operation_name == "head":
            operation.targets["rust-cli"].cli_full_command = "account show"
    elif resource_name == "container":
        if operation_name == "get":
            operation.targets["rust-cli"].cli_full_command = "object list"
        elif operation_name == "head":
            operation.targets["rust-cli"].cli_full_command = "container show"
    elif resource_name == "object":
        if operation_name == "get":
            operation.targets["rust-cli"].cli_full_command = "object download"
            operation.operation_type = "download"
        elif operation_name == "head":
            operation.targets["rust-cli"].cli_full_command = "object show"
        elif operation_name == "put":
            operation.targets["rust-cli"].cli_full_command = "object upload"
            operation.operation_type = "upload"

    return operation
