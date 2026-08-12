LOCAL_PATH := device/samsung/a02

# Architecture (32-bit only, jangan tempel apapun yang arm64)
PRODUCT_PROPERTY_OVERRIDES += \
    ro.zygote=zygote32

# Kernel
TARGET_KERNEL_SOURCE := kernel/samsung/a02
TARGET_KERNEL_CONFIG := a02_defconfig

# Rootdir
PRODUCT_PACKAGES += \
    init.a02.rc \
    fstab.mt6739

PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/rootdir/etc/init.a02.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.a02.rc \
    $(LOCAL_PATH)/rootdir/etc/fstab.mt6739:$(TARGET_COPY_OUT_VENDOR)/etc/fstab.mt6739

# Overlay
DEVICE_PACKAGE_OVERLAYS += $(LOCAL_PATH)/overlay

# Sepolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(LOCAL_PATH)/sepolicy/vendor
BOARD_PLAT_PRIVATE_SEPOLICY_DIR += $(LOCAL_PATH)/sepolicy/private

# Include vendor proprietary blobs
$(call inherit-product, vendor/samsung/a02/a02-vendor.mk)

# Include kernel config makefile
$(call inherit-product, device/samsung/a02/configs/kernel.mk)
