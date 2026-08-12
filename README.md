# Build OSS Android 13 (LineageOS 20 base) — SM-A022F (a02) — arm 32-bit

Target: MT6739, TARGET_ARCH = arm (32-bit), Android 13 (LineageOS 20 sources karena raw AOSP
gak punya HAL vendor MTK). Kernel & vendor blobs pake repo yang udah ada.

==================
Repo yang dipakai
==================
kernel      = https://github.com/rdbckp/a022f_kernel -b <branch_32bit_lo1_kamu>
vendor tree = https://github.com/rdbckp/vendor_a02 -b main   (isi lagi buat 13 kalau perlu bump)
device tree = repo baru ini -> device/samsung/a02
local manifest = .repo/local_manifests/a02.xml (sudah disiapkan di sini)

==================
1. Setup workspace
==================
mkdir lineage20 && cd lineage20
mkdir -p bin
curl https://storage.googleapis.com/git-repo-downloads/repo > bin/repo
chmod a+x bin/repo
echo 'export PATH=$HOME/lineage20/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
repo --version

==================
2. Init manifest LineageOS 20 (Android 13)
==================
repo init --depth=1 -u https://github.com/LineageOS/android.git -b lineage-20 --git-lfs
mkdir -p .repo/local_manifests
cp /path/to/a02.xml .repo/local_manifests/a02.xml
repo sync -c -j$(nproc) --force-sync --no-clone-bundle --no-tags

==================
3. Extract vendor blobs (dari vendor.tar.gz stok)
==================
cd device/samsung/a02
./extract-files.sh /path/ke/vendor.tar.gz
cd ../../..

==================
4. Struktur device tree (sudah dibuat di repo ini)
==================
device/samsung/a02/
├── AndroidProducts.mk
├── Android.mk
├── Android.bp
├── BoardConfig.mk
├── device.mk
├── lineage_a02.mk
├── vendorsetup.sh
├── extract-files.sh
├── setup-makefiles.sh
├── proprietary-files.txt
├── rootdir/
│   ├── Android.mk
│   └── etc/
│       ├── init.a02.rc
│       └── fstab.mt6739
├── sepolicy/
│   ├── vendor/
│   └── private/
├── overlay/
│   └── frameworks/base/core/res/res/values/config.xml
└── configs/
    └── kernel.mk

Kernel diclone terpisah ke kernel/samsung/a02 lewat local manifest (lihat a02.xml),
BUKAN disatuin manual di sini biar gampang update.

==================
5. Lunch & Build
==================
source build/envsetup.sh
lunch lineage_a02-userdebug
mka bacon
# hasil ada di out/target/product/a02/lineage-*-a02-signed.zip

==================
6. Kalau mau full GSI-style AOSP murni (tanpa Lineage)
==================
Ganti manifest init:
repo init --depth=1 -u https://android.googlesource.com/platform/manifest -b android-13.0.0_r74
Tapi lo perlu bikin sendiri device.mk yg inherit ke generic_arm.mk (bukan generic_arm64.mk)
dan siapin semua HAL vendor manual (audio, camera, gnss, dll) — jauh lebih ribet
dibanding pake LineageOS 20 base. Rekomendasi: pake opsi #2 (LineageOS 20) dulu.

==================
Catatan penting 32-bit vs 64-bit
==================
- BoardConfig.mk WAJIB: TARGET_ARCH := arm, TARGET_ARCH_VARIANT := armv7-a-neon,
  TARGET_CPU_ABI := armeabi-v7a, TARGET_CPU_ABI2 := armeabi — JANGAN campur arm64 apapun,
  atau boot bakal langsung bootloop kaya proyek 64-bit lo yang satu lagi.
- TARGET_COPY_OUT_VENDOR := vendor (fix yang sama kaya bug SHRP kemarin, wajib ada).
- Kalau pstore/log susah diambil pas debug, pola yang sama kaya waktu SHRP:
  pasang custom init logging + logcat ke /cache sebelum ADB daemon start.
