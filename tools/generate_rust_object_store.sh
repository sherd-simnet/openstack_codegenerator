#!/usr/bin/bash -e
#

WRK_DIR=wrk
METADATA=metadata
DST=~/workspace/github/gtema/openstack
NET_RESOURCES=(
  "account"
)

openstack-codegenerator --work-dir ${WRK_DIR} --target rust-sdk --metadata ${METADATA}/object-store_metadata.yaml --service object-store
# openstack-codegenerator --work-dir ${WRK_DIR} --target rust-cli --metadata ${METADATA}/object-store_metadata.yaml --service object-store


for resource in "${NET_RESOURCES[@]}"; do
  cp -av "${WRK_DIR}/rust/openstack_sdk/src/api/object_store/v1/${resource}" ${DST}/openstack_sdk/src/api/object_store/v1
  cp -av "${WRK_DIR}/rust/openstack_sdk/src/api/object_store/v1/${resource}.rs" ${DST}/openstack_sdk/src/api/object_store/v1
  #cp -av "${WRK_DIR}/rust/openstack_cli/src/object_store/v1/${resource}" ${DST}/openstack_cli/src/object_store/v1
  #cp -av "${WRK_DIR}/rust/openstack_cli/tests/object_store/v1/${resource}" ${DST}/openstack_cli/tests/object_store/v1
done;
