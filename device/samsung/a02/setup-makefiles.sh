#!/bin/bash
#
# setup-makefiles.sh — generate Android.bp/Android.mk otomatis buat blobs
# di vendor/samsung/a02 (dipanggil otomatis dari extract-files.sh via extract_utils.sh)
#
set -e

MY_DIR="$(cd "$(dirname "$0")" && pwd)"
LINEAGE_ROOT="$MY_DIR"/../../..

HELPER="$LINEAGE_ROOT"/vendor/lineage/build/tools/extract_utils.sh
source "$HELPER"

DEVICE=a02
VENDOR=samsung

setup_vendor "$DEVICE" "$VENDOR" "$LINEAGE_ROOT" false

write_headers "a02"
write_makefiles "$MY_DIR"/proprietary-files.txt true
write_footers
