LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),a02)
include $(call all-subdir-makefiles,$(LOCAL_PATH))
endif
