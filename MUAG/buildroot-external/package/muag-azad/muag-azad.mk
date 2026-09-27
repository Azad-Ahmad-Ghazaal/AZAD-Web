MUAG_AZAD_VERSION = 1.0
MUAG_AZAD_SITE = $(BR2_EXTERNAL_MUAG_PATH)/../azad
MUAG_AZAD_SITE_METHOD = local
MUAG_AZAD_DEPENDENCIES = python3

define MUAG_AZAD_INSTALL_TARGET_CMDS
	$(INSTALL) -d $(TARGET_DIR)/usr/share/muag/azad
	cp -a $(@D)/. $(TARGET_DIR)/usr/share/muag/azad/
	$(INSTALL) -D -m 0755 $(@D)/muag_action_bridge.py $(TARGET_DIR)/usr/bin/muag-action
	$(INSTALL) -D -m 0755 $(@D)/muag_actiond.py $(TARGET_DIR)/usr/bin/muag-actiond
	$(INSTALL) -D -m 0755 $(@D)/training/trace.py $(TARGET_DIR)/usr/bin/muag-azad-trace
	$(INSTALL) -D -m 0755 $(@D)/voice/muag_voice.py $(TARGET_DIR)/usr/bin/muag-voice
endef

$(eval $(generic-package))
