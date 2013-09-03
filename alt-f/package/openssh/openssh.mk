#############################################################
#
# openssh
#
#############################################################

OPENSSH_VERSION=6.1p1
OPENSSH_SITE=ftp://ftp.openbsd.org/pub/OpenBSD/OpenSSH/portable

OPENSSH_CONF_ENV = LD=$(TARGET_CC)
OPENSSH_CONF_OPT = --sysconfdir=/etc/ssh --with-privsep-path=/var/run/vsftpd \
	-disable-lastlog --disable-utmp --disable-utmpx --disable-wtmp --disable-wtmpx

OPENSSH_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) install

# The bellow dependency on dropbear is a fake. Dropbear installs ssh, scp, etc as a link
# to dropbear, so if it is installed after openssh it will override those binaries

OPENSSH_DEPENDENCIES = zlib openssl dropbear

$(eval $(call AUTOTARGETS,package,openssh))

ifneq ($(BR2_PACKAGE_OPENSSH_SFTP_ONLY),y)

$(OPENSSH_HOOK_POST_INSTALL):
	sed -i 's/#.*Ciphers /Ciphers aes128-cbc,/' $(TARGET_DIR)/etc/ssh/ssh_config
	touch $@

else

# this is a hack. Use AUTOTARGETS to do everything but install.
# At the build end, the post build hook runs, which installs just sftp-server
# and touchs the autotools dir as if a target install had been run.
# dont touch the dependency, otherwise a full install occurs.
# FIXME: use OPENSSH_TARGET_INSTALL_TARGET instead
#$(OPENSSH_HOOK_POST_BUILD):
#	#mkdir -p $(TARGET_DIR)/usr/libexec
#	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/lib
#	touch $(PROJECT_BUILD_DIR)/autotools-stamps/openssh_target_installed
##	touch $@ # dont! and don't remove me!

$(OPENSSH_TARGET_INSTALL_TARGET):
	$(INSTALL) -m 0755 $(OPENSSH_DIR)/sftp-server $(TARGET_DIR)/usr/lib
	touch $@

endif
