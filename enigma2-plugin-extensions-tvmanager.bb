SUMMARY = "TV Manager Plugin"
MAINTAINER = "Lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "CLOSED"

require conf/license/license-gplv2.inc

inherit gitpkgv allarch

SRCREV = "${AUTOREV}"
PV = "3.9+git${SRCPV}"
PKGV = "3.9+git${GITPKGV}"
PR = "r0"

SRC_URI = "git://github.com/Belfagor2005/tvManager.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

do_install() {
    install -d ${D}${libdir}/enigma2/python/Plugins/Extensions/tvManager
    cp -r ${S}/usr/lib/enigma2/python/Plugins/Extensions/tvManager/* \
          ${D}${libdir}/enigma2/python/Plugins/Extensions/tvManager/
}

FILES:${PN} = "${libdir}/enigma2/python/Plugins/Extensions/tvManager"