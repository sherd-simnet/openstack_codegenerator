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
from pathlib import Path
from unittest import mock

import fixtures

from codegenerator.common.schema import SpecSchema
from codegenerator.openapi.base import OpenStackServerSourceBase
from codegenerator.openapi.utils import merge_api_ref_doc

from ruamel.yaml.scalarstring import LiteralScalarString


class IronicGenerator(OpenStackServerSourceBase):
    URL_TAG_MAP = {
        # "/lbaas/listeners": "listeners",
        # "/lbaas/loadbalancers": "load-balancers",
        # "/lbaas/pools/{pool_id}/members": "members",
        # "/lbaas/pools": "pools",
        # "/lbaas/healthmonitors": "healthmonitors",
        # "/lbaas/l7policies/{l7policy_id}/rules": "l7-rules",
        # "/lbaas/l7policies": "l7-policies",
        # "/lbaas/quotas": "quotas",
        # "/lbaas/providers": "providers",
        # "/lbaas/flavorprofiles": "flavor-profiles",
        # "/lbaas/flavors": "flavors",
        # "/lbaas/availabilityzoneprofiles": "avaiability-zone-profiles",
        # "/lbaas/availabilityzones": "avaiability-zones",
        # "/lbaas/amphorae": "amphorae",
        # "/octavia/amphorae": "amphorae",
    }

    def __init__(self):
        pass
        # self.api_version = "2.27"
        # self.min_api_version = "2.0"

    #    def _fake_create_transport(self, url):
    #        import oslo_messaging as messaging
    #        from oslo_config import cfg
    #
    #        if url not in self._buses:
    #            self._buses[url] = messaging.get_rpc_transport(cfg.CONF, url=url)
    #        return self._buses[url]

    def _api_ver_major(self, ver):
        return ver.ver_major

    def _api_ver_minor(self, ver):
        return ver.ver_minor

    def _api_ver(self, ver):
        return (ver.ver_major, ver.ver_minor)

    def _build_routes(self, mapper, node, path=""):
        resource: str | None = None
        # Construct resource name from the path
        parent = path.split("/")[-1]
        if parent == "v1":
            resource = ""
        elif parent.endswith("ies"):
            resource = parent[0 : len(parent) - 3] + "y"
        elif parent in ["allocation", "history", "vmedia", "chassis", "bios"]:
            resource = parent
        else:
            resource = parent[0:-1]

        for part in [x for x in dir(node) if callable(getattr(node, x))]:
            # Iterate over functions to find what is exposed on the current
            # level
            obj = getattr(node, part)
            _pecan = getattr(obj, "_pecan", None)
            exposed = getattr(obj, "exposed", None)
            if _pecan and exposed:
                # Only whatever is pecan exposed is of interest
                conditions = {}
                action = None
                url = path
                # resource = None
                # parent = url.split("/")[-1]
                # if path.startswith("/v2/lbaas/quotas"):
                #     # Hack path parameter name for quotas
                #     resource = "project"
                # Identify the action from function name
                # https://pecan.readthedocs.io/en/latest/rest.html#url-mapping
                if part == "get_one":
                    conditions["method"] = ["GET"]
                    action = "show"
                    url += f"/{{{resource}_id}}"
                elif part == "get_all":
                    conditions["method"] = ["GET"]
                    action = "list"
                elif part == "get":
                    conditions["method"] = ["GET"]
                    action = "get"
                    # "Get" is tricky, it can be normal and root, so need to inspect params
                    sig = inspect.signature(obj)
                    for pname, pval in sig.parameters.items():
                        if "id" in pname and pval.default == pval.empty:
                            url += f"/{{{resource}_id}}"
                elif part == "post":
                    conditions["method"] = ["POST"]
                    action = "create"
                    # url += f"/{{{resource}_id}}"
                elif part == "put":
                    conditions["method"] = ["PUT"]
                    action = "update"
                    url += f"/{{{resource}_id}}"
                elif part == "patch":
                    conditions["method"] = ["PATCH"]
                    action = "update"
                    url += f"/{{{resource}_id}}"
                elif part == "delete":
                    conditions["method"] = ["DELETE"]
                    action = "delete"
                    url += f"/{{{resource}_id}}"
                elif part in getattr(node, "_custom_actions", {}):
                    conditions["method"] = getattr(
                        node, "_custom_actions", {}
                    )[part]
                    action = part
                    url += f"/{part}"

                if action:
                    # If we identified method as "interesting" register it into
                    # the routes mapper
                    mapper.connect(
                        None,
                        url,
                        controller=obj,
                        action=action,
                        conditions=conditions,
                    )

        for subcontroller, v in getattr(
            node, "_subcontroller_map", {}
        ).items():
            if resource:
                subpath = f"{path}/{{{resource}_id}}/{subcontroller}"
            else:
                subpath = f"{path}/{subcontroller}"

            self._build_routes(mapper, v, subpath)

        return

    def generate(self, target_dir, args):
        proc = Process(target=self._generate, args=[target_dir, args])
        proc.start()
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError("Error generating Octavia OpenAPI schema")

    def _generate(self, target_dir, args):
        from ironic.api.controllers.v1 import versions
        from ironic.api.controllers import root as root_controller
        from ironic.api.controllers import v1

        from pecan import make_app as pecan_make_app
        from routes import Mapper

        self.api_version = versions.max_version_string()
        self.min_api_version = versions.min_version_string()

        work_dir = Path(target_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        impl_path = Path(
            work_dir,
            "openapi_specs",
            "baremetal",
            f"v{self.api_version}.yaml",
        )
        impl_path.parent.mkdir(parents=True, exist_ok=True)
        openapi_spec = self.load_openapi(Path(impl_path))
        if not openapi_spec:
            openapi_spec = SpecSchema(
                info=dict(
                    title="OpenStack Baremetal API",
                    description=LiteralScalarString(
                        "Baremetal API provided by Ironic service"
                    ),
                    version=self.api_version,
                ),
                openapi="3.1.0",
                security=[{"ApiKeyAuth": []}],
                components=dict(
                    securitySchemes={
                        "ApiKeyAuth": {
                            "type": "apiKey",
                            "in": "header",
                            "name": "X-Auth-Token",
                        }
                    },
                ),
            )

        self.app = pecan_make_app(root_controller.RootController())
        self.root = self.app.application.root
        mapper = Mapper()
        self._build_routes(mapper, v1.Controller, "/v1")

        for route in mapper.matchlist:
            self._process_route(route, openapi_spec, framework="pecan")

        if args.api_ref_src:
            merge_api_ref_doc(
                openapi_spec, args.api_ref_src, allow_strip_version=False
            )

        self.dump_openapi(openapi_spec, Path(impl_path), args.validate)

        lnk = Path(impl_path.parent, "v1.yaml")
        lnk.unlink(missing_ok=True)
        lnk.symlink_to(impl_path.name)

        return impl_path
