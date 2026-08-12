#!/usr/bin/env python3
"""
gen_vendor_tree.py
------------------
Narik semua file dari hasil extract vendor.tar.gz, taro ke
<out>/proprietary/<relpath>, terus auto-generate:
  - <out>/proprietary-files.txt
  - <out>/Android.bp   (cc_prebuilt_library_shared / cc_prebuilt_binary / prebuilt_etc)

Simple heuristic-based, BUKAN pengganti extract_utils.sh punya LineageOS,
tapi cukup buat dapetin skeleton makefile dari isi vendor.tar.gz apa adanya
tanpa perlu full source tree ke-sync di runner.

Filter arch (--arch-filter 32) bakal SKIP:
  lib64/, bin64/, apapun yang ada '64' di path top-level libnya
biar konsisten sama BoardConfig 32-bit (TARGET_ARCH := arm).
"""
import argparse
import os
import shutil
import stat
import sys

SKIP_DIRNAMES_32 = {"lib64", "bin64"}

def is_elf_shared_lib(path):
    return path.endswith(".so") or ".so." in os.path.basename(path)

def is_executable(path):
    try:
        st = os.stat(path)
        return bool(st.st_mode & stat.S_IXUSR) and not os.path.isdir(path)
    except OSError:
        return False

def should_skip(relpath, arch_filter):
    if arch_filter != "32":
        return False
    parts = relpath.split(os.sep)
    return any(p in SKIP_DIRNAMES_32 for p in parts)

def module_name_from_path(relpath):
    base = os.path.basename(relpath)
    name, _ = os.path.splitext(base)
    return name

def classify(relpath):
    if is_elf_shared_lib(relpath):
        return "lib"
    if relpath.startswith(os.path.join("bin", "")) or "/bin/" in relpath:
        return "bin"
    return "etc"

def out_partition_and_subpath(relpath):
    """
    Asumsikan struktur hasil extract vendor.tar.gz sama kaya root /vendor
    (karena ini emang tar dari partisi vendor yang lagi jalan).
    Balikin ("vendor", subpath) supaya proprietary-files.txt & PRODUCT_COPY_FILES
    konsisten sama TARGET_COPY_OUT_VENDOR := vendor.
    """
    return "vendor", relpath

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder hasil extract vendor.tar.gz")
    ap.add_argument("--out", required=True, help="target device vendor dir, misal vendor/samsung/a02")
    ap.add_argument("--arch-filter", default="32", choices=["32", "all"])
    args = ap.parse_args()

    src = args.src
    out = args.out
    proprietary_dir = os.path.join(out, "proprietary")
    os.makedirs(proprietary_dir, exist_ok=True)

    entries = []          # (relpath, module_type)
    copied = 0
    skipped = 0

    for root, dirs, files in os.walk(src):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, src)

            if should_skip(rel, args.arch_filter):
                skipped += 1
                continue

            dst = os.path.join(proprietary_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(full, dst)
            copied += 1

            entries.append((rel, classify(rel)))

    entries.sort(key=lambda x: x[0])

    # ---- proprietary-files.txt ----
    prop_txt_path = os.path.join(out, "proprietary-files.txt")
    with open(prop_txt_path, "w") as fh:
        fh.write("# Auto-generated oleh gen_vendor_tree.py dari vendor.tar.gz\n")
        fh.write("# Review manual sebelum dipake buat build asli.\n\n")
        partition, _ = out_partition_and_subpath("")
        for rel, _mtype in entries:
            _, subpath = out_partition_and_subpath(rel)
            fh.write(f"{partition}/{subpath}\n")

    # ---- Android.bp ----
    bp_path = os.path.join(out, "Android.bp")
    seen_names = set()
    with open(bp_path, "w") as fh:
        fh.write("// Auto-generated oleh gen_vendor_tree.py — REVIEW sebelum dipakai.\n\n")
        for rel, mtype in entries:
            name = module_name_from_path(rel)
            # avoid duplicate module names
            uniq_name = name
            i = 2
            while uniq_name in seen_names:
                uniq_name = f"{name}_{i}"
                i += 1
            seen_names.add(uniq_name)

            _, subpath = out_partition_and_subpath(rel)
            rel_bp_src = os.path.join("proprietary", rel).replace(os.sep, "/")
            sub_dir = os.path.dirname(subpath).replace(os.sep, "/")

            if mtype == "lib":
                fh.write(f'''cc_prebuilt_library_shared {{
    name: "{uniq_name}",
    owner: "samsung",
    srcs: ["{rel_bp_src}"],
    compile_multilib: "32",
    check_elf_files: false,
    prefer: true,
    vendor: true,
    strip: {{ none: true }},
}}

''')
            elif mtype == "bin":
                fh.write(f'''cc_prebuilt_binary {{
    name: "{uniq_name}",
    owner: "samsung",
    srcs: ["{rel_bp_src}"],
    compile_multilib: "32",
    check_elf_files: false,
    vendor: true,
    strip: {{ none: true }},
}}

''')
            else:
                fh.write(f'''prebuilt_etc {{
    name: "{uniq_name}",
    owner: "samsung",
    src: "{rel_bp_src}",
    sub_dir: "{sub_dir}",
    vendor: true,
}}

''')

    print(f"Copied {copied} files, skipped {skipped} (arch-filter={args.arch_filter})")
    print(f"Wrote {prop_txt_path}")
    print(f"Wrote {bp_path}")

if __name__ == "__main__":
    main()
