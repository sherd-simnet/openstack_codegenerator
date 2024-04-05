#!/usr/bin/bash -e
#

WRK_DIR=wrk
METADATA=metadata
DST=~/workspace/github/gtema/openstack
NET_RESOURCES=(
  "amphorae"
  "availability_zone"
  "availability_zone_profile"
  "flavor"
  "flavor_profile"
  "healthmonitor"
  "l7policy"
  "listener"
  "loadbalancer"
  "pool"
  "provider"
  "quota"
  "version"
)

openstack-codegenerator --work-dir ${WRK_DIR} --target rust-sdk --metadata ${METADATA}/load-balancer_metadata.yaml --service load-balancer
openstack-codegenerator --work-dir ${WRK_DIR} --target rust-cli --metadata ${METADATA}/load-balancer_metadata.yaml --service load-balancer


for resource in "${NET_RESOURCES[@]}"; do
  cp -av "${WRK_DIR}/rust/openstack_sdk/src/api/load_balancer/v2/${resource}" ${DST}/openstack_sdk/src/api/load_balancer/v2
  cp -av "${WRK_DIR}/rust/openstack_sdk/src/api/load_balancer/v2/${resource}.rs" ${DST}/openstack_sdk/src/api/load_balancer/v2
  cp -av "${WRK_DIR}/rust/openstack_cli/src/load_balancer/v2/${resource}" ${DST}/openstack_cli/src/load_balancer/v2
  cp -av "${WRK_DIR}/rust/openstack_cli/tests/load_balancer/v2/${resource}" ${DST}/openstack_cli/tests/load_balancer/v2
done;
