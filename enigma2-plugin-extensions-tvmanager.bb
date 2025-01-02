SUMMARY = "tvManager"
MAINTAINER = "lululla"
SECTION = "base"
PRIORITY = "required"
LICENSE = "proprietary"

inherit gitpkgv allarch

require conf/license/license-gplv2.inc

inherit gitpkgv
SRCREV = "${AUTOREV}"
PV = "1.0+git${SRCPV}"
PKGV = "1.0+git${GITPKGV}"
VER ="2.4"
PR = "r0"

SRC_URI="git://github.com/Belfagor2005/tvManager.git;protocol=https;branch=main"

S = "${WORKDIR}/git"

FILES_${PN} = "/usr/*"

do_install() {
    cp -rp ${S}/usr* ${D}/ 
}
