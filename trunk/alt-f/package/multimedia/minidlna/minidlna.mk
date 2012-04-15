#############################################################
#
# minidlna
#
#############################################################

MINIDLNA_VERSION = 1.0.24
MINIDLNA_SOURCE = minidlna_$(MINIDLNA_VERSION)_src.tar.gz
MINIDLNA_SITE = http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/minidlna
#MINIDLNA_SITE = http://downloads.sourceforge.net/project/minidlna/minidlna/$(MINIDLNA_VERSION)
MINIDLNA_AUTORECONF = NO
MINIDLNA_INSTALL_STAGING = NO
MINIDLNA_INSTALL_TARGET = YES
MINIDLNA_LIBTOOL_PATCH = NO
	
MINIDLNA_DEPENDENCIES = uclibc libexif jpeg libid3tag flac libvorbis sqlite ffmpeg

$(eval $(call AUTOTARGETS,package/multimedia,minidlna))
	
$(MINIDLNA_HOOK_POST_EXTRACT):
	touch $(MINIDLNA_DIR)/configure
	chmod +x $(MINIDLNA_DIR)/configure
	touch $@