MUAG_SHELL_VERSION = 1.0
MUAG_SHELL_SITE = $(BR2_EXTERNAL_MUAG_PATH)/../ui/shell
MUAG_SHELL_SITE_METHOD = local
MUAG_SHELL_DEPENDENCIES =

define MUAG_SHELL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/muag-shell.py $(TARGET_DIR)/usr/bin/muag-shell
	$(INSTALL) -D -m 0644 $(@D)/index.html $(TARGET_DIR)/usr/share/muag/shell/index.html
endef

$(eval $(generic-package))
