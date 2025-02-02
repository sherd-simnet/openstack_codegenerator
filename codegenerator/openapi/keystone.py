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
import inspect
from multiprocessing import Process
import logging
from pathlib import Path

from ruamel.yaml.scalarstring import LiteralScalarString

from codegenerator.common.schema import ParameterSchema
from codegenerator.common.schema import PathSchema
from codegenerator.common.schema import SpecSchema
from codegenerator.common.schema import TypeSchema
from codegenerator.openapi.base import OpenStackServerSourceBase
from codegenerator.openapi.keystone_schemas import application_credential
from codegenerator.openapi.keystone_schemas import auth
from codegenerator.openapi.keystone_schemas import common
from codegenerator.openapi.keystone_schemas import domain
from codegenerator.openapi.keystone_schemas import endpoint
from codegenerator.openapi.keystone_schemas import federation
from codegenerator.openapi.keystone_schemas import group
from codegenerator.openapi.keystone_schemas import project
from codegenerator.openapi.keystone_schemas import region
from codegenerator.openapi.keystone_schemas import role
from codegenerator.openapi.keystone_schemas import service
from codegenerator.openapi.keystone_schemas import user
from codegenerator.openapi.utils import merge_api_ref_doc
from codegenerator.openapi.utils import rst_to_md


class KeystoneGenerator(OpenStackServerSourceBase):
    URL_TAG_MAP = {
        "/domains/config": "domain-configuration",
        "/domains/{domain_id}/config": "domain-configuration",
        "/domains/{domain_id}/groups/{group_id}/roles": "roles",
        "/domains/{domain_id}/users/{user_id}/roles": "roles",
    }

    RESOURCE_MODULES = [
        application_credential,
        auth,
        common,
        domain,
        endpoint,
        federation,
        group,
        project,
        region,
        role,
        service,
        user,
    ]

    def __init__(self):
        self.api_version = "3.0"
        self.min_api_version = "3.14"

    def _api_ver_major(self, ver):
        return ver._ver_major

    def _api_ver_minor(self, ver):
        return ver._ver_minor

    def _api_ver(self, ver):
        return (ver._ver_major, ver._ver_minor)

    def generate(self, target_dir, args):
        proc = Process(target=self._generate, args=[target_dir, args])
        proc.start()
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError("Error generating Keystone OpenAPI schema")

    def _generate(self, target_dir, args, *pargs, **kwargs):
        from keystone.server.flask import application
        from keystone import version as keystone_version

        self.app = application.application_factory()
        self.router = self.app.url_map
        self.api_version = keystone_version.release_string()[1:]

        work_dir = Path(target_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        impl_path = Path(
            work_dir, "openapi_specs", "identity", f"v{self.api_version}.yaml"
        )
        impl_path.parent.mkdir(parents=True, exist_ok=True)

        openapi_spec = self.load_openapi(impl_path)
        if not openapi_spec:
            openapi_spec = SpecSchema(
                info={
                    "title": "OpenStack Identity API",
                    "description": LiteralScalarString(
                        "Identity API provided by Keystone service"
                    ),
                    "version": self.api_version,
                },
                openapi="3.1.0",
                security=[{"ApiKeyAuth": []}],
                components={
                    "securitySchemes": {
                        "ApiKeyAuth": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "X-Auth-Token",
                        }
                    },
                    "headers": {
                        "X-Auth-Token": {
                            "description": "A valid authentication token",
                            "schema": {"type": "string", "format": "secret"},
                        },
                        "X-Subject-Token": {
                            "description": "A valid authentication token",
                            "schema": {"type": "string", "format": "secret"},
                        },
                        "Openstack-Auth-Receipt": {
                            "description": "The auth receipt. A partially successful authentication response returns the auth receipt ID in this header rather than in the response body.",
                            "schema": {"type": "string"},
                        },
                    },
                    "parameters": {
                        "X-Auth-Token": {
                            "in": "header",
                            "name": "X-Auth-Token",
                            "description": "A valid authentication token",
                            "schema": {"type": "string", "format": "secret"},
                        },
                        "X-Subject-Token": {
                            "in": "header",
                            "name": "X-Subject-Token",
                            "description": "The authentication token. An authentication response returns the token ID in this header rather than in the response body.",
                            "schema": {"type": "string", "format": "secret"},
                            "required": True,
                        },
                    },
                },
            )

        for route in self.router.iter_rules():
            if route.rule.startswith("/static"):
                continue

            self._process_route_keystone(route, openapi_spec)

        self._sanitize_param_ver_info(openapi_spec, self.min_api_version)

        if args.api_ref_src:
            merge_api_ref_doc(
                openapi_spec, args.api_ref_src, allow_strip_version=False
            )

        self.dump_openapi(openapi_spec, impl_path, args.validate)

        lnk = Path(impl_path.parent, "v3.yaml")
        lnk.unlink(missing_ok=True)
        lnk.symlink_to(impl_path.name)

        return impl_path

    def _process_route_keystone(self, route, openapi_spec):
        args = route.arguments
        # ep = route.endpoint
        view = self.app.view_functions[route.endpoint]
        controller = None
        if hasattr(view, "view_class"):
            controller = view.view_class

        path: str = ""
        path_elements: list[str] = []
        operation_spec = None

        for part in route.rule.split("/"):
            if not part:
                continue
            if part.startswith("<"):
                param = part.strip("<>").split(":")
                path_elements.append("{" + param[-1] + "}")
            else:
                path_elements.append(part)

        path = "/" + "/".join(path_elements)
        # Get rid of /v3 for further processing
        path_elements = path_elements[1:]

        # Build path parameters (/foo/{foo_id}/bar/{id} => $foo_id, $foo_bar_id)
        # Since for same path we are here multiple times check presence of
        # parameter before adding new params
        path_params: list[ParameterSchema] = []
        path_resource_names: list[str] = []
        operation_tags = self._get_tags_for_url(path)
        for path_element in path_elements:
            if "{" not in path_element:
                path_resource_names.append(path_element.replace("-", "_"))
        for path_element in path_elements:
            if "{" in path_element:
                param_name = path_element.strip("{}")
                global_param_name = (
                    "_".join(path_resource_names) + f"_{param_name}"
                )
                param_ref_name = f"#/components/parameters/{global_param_name}"
                # Ensure reference to the param is in the path_params
                if param_ref_name not in [k.ref for k in list(path_params)]:
                    path_params.append(ParameterSchema(ref=param_ref_name))
                # Ensure global parameter is present
                path_param = ParameterSchema(
                    location="path", name=param_name, required=True
                )
                # openapi_spec.components.parameters.setdefault(global_param_name, dict())
                if not path_param.description:
                    path_param.description = LiteralScalarString(
                        f"{param_name} parameter for {path} API"
                    )
                # We can only assume the param type. For path it is logically a string only
                path_param.type_schema = TypeSchema(type="string")
                # For non /users/{id} urls link user_id path attribute to the user resource
                if path_param.name == "user_id" and path_resource_names != [
                    "users"
                ]:
                    if not path_param.openstack:
                        path_param.openstack = {}
                    path_param.openstack["resource_link"] = (
                        "identity/v3/user.id"
                    )
                if path_param.name == "domain_id" and path_resource_names != [
                    "domains"
                ]:
                    if not path_param.openstack:
                        path_param.openstack = {}
                    path_param.openstack["resource_link"] = (
                        "identity/v3/domain.id"
                    )
                openapi_spec.components.parameters[global_param_name] = (
                    path_param
                )
        if len(path_elements) == 0:
            path_resource_names.append("root")
        elif path_elements[-1].startswith("{"):
            rn = path_resource_names[-1]
            if rn.endswith("ies"):
                rn = rn.replace("ies", "y")
            else:
                rn = rn.rstrip("s")
            path_resource_names[-1] = rn
        # Hack resource element names for domain configs
        if path in [
            "/v3/domains/config/{group}/default",
            "/v3/domains/{domain_id}/config/{group}",
        ]:
            path_resource_names = ["domains", "config", "group"]
        elif path in [
            "/v3/domains/config/{group}/{option}/default",
            "/v3/domains/{domain_id}/config/{group}/{option}",
        ]:
            path_resource_names = ["domains", "config", "group", "option"]

        path_spec = openapi_spec.paths.setdefault(
            path, PathSchema(parameters=path_params)
        )
        # Set operationId
        if path == "/":
            operation_id_prefix = "versions"
        elif path == "/v3":
            operation_id_prefix = "version"
        else:
            operation_id_prefix = "/".join(
                [x.strip("{}") for x in path_elements]
            )
        for method in route.methods:
            if method == "OPTIONS":
                # Not sure what should be done with it
                continue
            if controller:
                func = getattr(
                    controller, method.replace("HEAD", "GET").lower(), None
                )
            else:
                func = view
            # Set operationId
            operation_id = operation_id_prefix + f":{method.lower()}"  # noqa
            # There is a variety of operations that make absolutely no sense and
            # are just not filtered by Keystone itself
            if path == "/v3/users/{user_id}/password" and method in [
                "GET",
                "HEAD",
            ]:
                continue

            # Current Keystone code is having a bug of exposing same controller
            # API for both /RESOURCE and /RESOURCE/{ID}. Routing is then
            # failing to invoke the method because of missing parameter, so
            # analyse and skip those now.
            if not func:
                continue
            sig = inspect.signature(func)
            for param in args:
                if param not in sig.parameters:
                    logging.warn(
                        "Skipping %s:%s because controller does not support parameter %s",
                        path,
                        method,
                        param,
                    )
                    func = None
                    break
            for param in sig.parameters.values():
                if (
                    param.name not in ["self"]
                    and param.default == param.empty
                    and param.name not in args
                ):
                    # Param with no default is not a path argument
                    logging.warn(
                        "Skipping %s:%s because controller requires parameter %s not present in path",
                        path,
                        method,
                        param,
                    )
                    func = None
                    break

            if not func:
                continue

            operation_spec = getattr(path_spec, method.lower())
            if not operation_spec.operationId:
                operation_spec.operationId = operation_id
            doc = inspect.getdoc(func)
            if not operation_spec.description:
                operation_spec.description = LiteralScalarString(
                    doc or f"{method} operation on {path}"
                )
            operation_spec.tags.extend(operation_tags)
            operation_spec.tags = list(set(operation_spec.tags))

            self.process_operation_keystone(
                func,
                path,
                openapi_spec,
                operation_spec,
                path_resource_names,
                method=method,
            )

        return operation_spec

    def process_operation_keystone(
        self,
        func,
        path,
        openapi_spec,
        operation_spec,
        path_resource_names,
        *,
        method=None,
    ):
        logging.info("Operation: %s [%s]", path, method)
        doc = inspect.getdoc(func)
        if doc and not operation_spec.description:
            doc = rst_to_md(doc)
            operation_spec.description = LiteralScalarString(doc)

        query_params_versions = []
        body_schemas = []
        expected_errors = ["404"]
        response_code = None
        start_version = None
        end_version = None
        ser_schema: dict | None = {}

        (query_params_versions, body_schemas, ser_schema, expected_errors) = (
            self._process_decorators(
                func,
                path_resource_names,
                openapi_spec,
                method,
                start_version,
                end_version,
                None,
            )
        )

        if query_params_versions:
            so = sorted(
                query_params_versions,
                key=lambda d: (
                    tuple(map(int, d[1].split("."))) if d[1] else (0, 0)
                ),
            )
            for data, min_ver, max_ver in so:
                self.process_query_parameters(
                    openapi_spec,
                    operation_spec,
                    path_resource_names,
                    data,
                    min_ver,
                    max_ver,
                )

        if method in ["PUT", "POST", "PATCH"]:
            self.process_body_parameters(
                openapi_spec,
                operation_spec,
                path_resource_names,
                body_schemas,
                None,
                method,
            )

        responses_spec = operation_spec.responses
        # Errors
        for error in ["403", "404"]:
            responses_spec.setdefault(str(error), {"description": "Error"})
        # Response data
        if method == "POST":
            response_code = "201"
        if method == "PUT":
            response_code = "201"
        elif method == "DELETE":
            response_code = "204"
        else:
            response_code = "200"
        if path == "/v3/projects/{project_id}/tags/{value}" and method in [
            "GET",
            "HEAD",
        ]:
            response_code = "204"
        elif path in [
            "/v3/projects/{project_id}/users/{user_id}/roles/{role_id}",
            "/v3/domains/{project_id}/users/{user_id}/roles/{role_id}",
        ] and method in ["GET", "HEAD", "PUT"]:
            response_code = "204"
        elif path in [
            "/v3/projects/{project_id}/groups/{user_id}/roles/{role_id}",
            "/v3/domains/{project_id}/groups/{user_id}/roles/{role_id}",
        ] and method in ["GET", "HEAD", "PUT"]:
            response_code = "204"
        elif path == "/v3/users/{user_id}/password" and method == "POST":
            response_code = "204"
        rsp = responses_spec.setdefault(response_code, {"description": "Ok"})
        if response_code != "204" and method not in ["DELETE", "HEAD"]:
            # Arrange response placeholder
            schema_name = (
                "".join([x.title() for x in path_resource_names])
                + method.title()
                + "Response"
            )
            (schema_ref, mime_type) = self._get_schema_ref(
                openapi_spec,
                schema_name,
                description=f"Response of the {operation_spec.operationId} operation",
                schema_def=ser_schema,
            )

            if schema_ref:
                rsp["content"] = {mime_type: {"schema": {"$ref": schema_ref}}}

        if path == "/v3/auth/tokens":
            rsp_headers = rsp.setdefault("headers", {})
            if method == "POST":
                openapi_spec.components.headers["X-Subject-Token"] = {
                    "description": "API Authorization token",
                    "schema": {"type": "string"},
                }
                rsp_headers.setdefault(
                    "X-Subject-Token",
                    {"$ref": "#/components/headers/X-Subject-Token"},
                )
                operation_spec.security = []
            elif method == "GET":
                operation_spec.parameters.append(
                    ParameterSchema(
                        ref="#/components/parameters/X-Subject-Token"
                    )
                )
                rsp_headers.setdefault(
                    "X-Subject-Token",
                    {"$ref": "#/components/headers/X-Subject-Token"},
                )

        # Ensure operation tags are existing
        for tag in operation_spec.tags:
            if tag not in [x["name"] for x in openapi_spec.tags]:
                openapi_spec.tags.append({"name": tag, "description": None})

        self._post_process_operation_hook(
            openapi_spec, operation_spec, path=path
        )

    def _post_process_operation_hook(
        self, openapi_spec, operation_spec, path: str | None = None
    ):
        """Hook to allow service specific generator to modify details"""
        for resource_mod in self.RESOURCE_MODULES:
            hook = getattr(resource_mod, "_post_process_operation_hook", None)
            if hook:
                hook(openapi_spec, operation_spec, path=path)

    def _get_schema_ref(
        self,
        openapi_spec,
        name,
        description=None,
        schema_def=None,
        action_name=None,
    ):
        # Invoke modularized schema _get_schema_ref
        for resource_mod in self.RESOURCE_MODULES:
            hook = getattr(resource_mod, "_get_schema_ref", None)
            if hook:
                (ref, mime_type, matched) = hook(
                    openapi_spec, name, description, schema_def, action_name
                )
                if matched:
                    return (ref, mime_type)

        # Default
        (ref, mime_type) = super()._get_schema_ref(
            openapi_spec,
            name,
            description,
            schema_def=schema_def,
            action_name=action_name,
        )
        return (ref, mime_type)
