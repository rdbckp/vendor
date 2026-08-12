#!/bin/bash
#
# extract-files.sh — narik proprietary blobs dari vendor.tar.gz stok
# yang udah lo repack sebelumnya (repo rdbckp/vendor), ke vendor/samsung/a02.
#
set -e

DEVICE=a02
VENDOR=samsung

MY_DIR="$(cd "$(dirname "$0")" && pwd)"
LINEAGE_ROOT="$MY_DIR"/../../..

HELPER="$LINEAGE_ROOT"/vendor/lineage/build/tools/extract_utils.sh
if [ ! -f "$HELPER" ]; then
    echo "Gak nemu extract_utils.sh, pastiin vendor/lineage udah di-sync."
    exit 1
fi
source "$HELPER"

setup_vendor "$DEVICE" "$VENDOR" "$LINEAGE_ROOT" true

extract "$MY_DIR"/proprietary-files.txt "$SRC" "$KANG" --section "${SECTION}"
