%define version 4.0
%define releasedate 20110503
%define release %mkrel 2.%{releasedate}.3

Name:		foomatic-db
Version:	%{version}
Release:	%{release}
Epoch:		1
Summary:	Foomatic printer/driver database
License:	GPLv2 and MIT
Group:		System/Servers
Url:		http://www.linuxprinting.org/
Source:		http://www.linuxprinting.org/download/foomatic/%{name}-%{version}-%{releasedate}.tar.gz
# Perl script to clean up Manufacturer entries in the PPD files, so that
# drivers are sorted by the printer manufacturer in the graphical frontends
Source2:	cleanppd.pl.bz2
Patch0:		foomatic-db-20100218-cp_argument_list_too_long.diff
Requires:	foomatic-db-engine
Conflicts:	postscript-ppds <= 2006-1mdk
Conflicts:	cups-drivers-foo2zjs < 0.0-0.20091014.1
BuildArch:	noarch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cups
BuildRequires:	cups-common
BuildRequires:	foomatic-db-engine
BuildRoot:	%_tmppath/%name-%version-%release-root

%description
Foomatic is a comprehensive, spooler-independent database of printers,
printer drivers, and driver descriptions. It contains utilities to
generate PPD (Postscript Printer Description) files and printer queues
for CUPS, LPD, GNUlpr, LPRng, PPR, and PDQ using the database. There
is also the possibility to read the PJL options out of PJL-capable
laser printers and take them into account at the driver description
file generation.

There are spooler-independent command line interfaces to manipulate
queues (foomatic-configure) and to print files/manipulate jobs
(foomatic printjob).
 
This package is the Foomatic database, an XML database containing
information about the capabilities of near 1000 printers and around
250 drivers. Especially it contains the information how and with which
options the drivers have to be executed.

%prep

##### FOOMATIC

# Source trees for installation
%setup -q -n %{name}-%{releasedate}
%patch0 -p0

%build
# Makefile generation ("./make_configure" for CVS snapshots)
./make_configure
# Fix for lib64 architectures, avoid patch
perl -pi -e "s@/usr/lib/(cups|pdq|ppr)@%{_libdir}/\1@g" configure

# We do not compress the PPDs now, so that we can do a clean-up
%configure --disable-gzip-ppds

# "make" is not needed for this package, there is nothing to build

# Delete drivers which are not on the distro (obsolete drivers which are
# replaced by a new driver with a different name)
# "stp" replaced by "gimp-print"/"gutenprint"
rm -f db/source/driver/stp.xml
# "cZ11" replaced by "cZ11somsom"
rm -f db/source/driver/cZ11.xml
# "cZ11somsom" replaced by "lz11"
rm -f db/source/driver/cZ11somsom.xml
# "hpdj" replaced by "pcl3"
rm -f db/source/driver/hpdj.xml
# "lxm3200[mcp]" replaced by "lxm3200"
rm -f db/source/driver/lxm3200[mcp].xml
# "lxm3200" replaced by "lxm3200-tweaked"
rm -f db/source/driver/lxm3200.xml
# Japanese drivers which are not in our GhostScript
rm -f db/source/driver/bjc800j.xml
rm -f db/source/driver/bj10.xml

# These drivers come with their own Foomatic data. Remove the files
# from this package
rm -f db/source/*/gimp-print*.xml
rm -f db/source/*/gutenprint*.xml
rm -f db/source/*/foo2*.xml
rm -f db/source/*/lz11*.xml
rm -f db/source/*/m2300w*.xml
rm -f db/source/*/m2400w*.xml
rm -f db/source/[do]*/*[Pp]touch*.xml

# foo2zjs files
rm -f \
	db/source/printer/HP-Color_LaserJet_1500.xml \
	db/source/printer/HP-Color_LaserJet_1600.xml \
	db/source/printer/HP-Color_LaserJet_2600n.xml \
	db/source/printer/HP-LaserJet_1000.xml \
	db/source/printer/HP-LaserJet_1005.xml \
	db/source/printer/HP-LaserJet_1020.xml \
	db/source/printer/HP-LaserJet_1022.xml \
	db/source/printer/HP-LaserJet_M1005_MFP.xml \
	db/source/printer/Minolta-magicolor_2300_DL.xml \
	db/source/printer/Minolta-magicolor_2430_DL.xml \
	db/source/printer/Samsung-CLP-300.xml \
	db/source/printer/Samsung-CLP-600.xml \
	db/source/printer/Xerox-Phaser-6115MFP.xml

# m2300w files
rm -f \
	db/source/printer/Minolta-magicolor_2300W.xml \
	db/source/printer/Minolta-magicolor_2400W.xml

# ptouch files
rm -f \
	db/source/printer/Brother-PT-1500PC.xml \
	db/source/printer/Brother-PT-18R.xml \
	db/source/printer/Brother-PT-1950.xml \
	db/source/printer/Brother-PT-1950VP.xml \
	db/source/printer/Brother-PT-1960.xml \
	db/source/printer/Brother-PT-2420PC.xml \
	db/source/printer/Brother-PT-2450DX.xml \
	db/source/printer/Brother-PT-2500PC.xml \
	db/source/printer/Brother-PT-2600.xml \
	db/source/printer/Brother-PT-2610.xml \
	db/source/printer/Brother-PT-3600.xml \
	db/source/printer/Brother-PT-550A.xml \
	db/source/printer/Brother-PT-9200DX.xml \
	db/source/printer/Brother-PT-9200PC.xml \
	db/source/printer/Brother-PT-9400.xml \
	db/source/printer/Brother-PT-9500PC.xml \
	db/source/printer/Brother-PT-9600.xml \
	db/source/printer/Brother-PT-PC.xml \
	db/source/printer/Brother-QL-500.xml \
	db/source/printer/Brother-QL-550.xml \
	db/source/printer/Brother-QL-650TD.xml

# Delete drivers with empty command line prototype, they would give
# unusable printer/driver combos.
FOOMATICDB=`pwd` %{_sbindir}/foomatic-cleanupdrivers

# Correct recommended driver "gimp-print" or "gutenprint", must be 
# "gutenprint-ijs.5.0".
for f in db/source/printer/*.xml; do
	perl -p -i -e 's:<driver>(gimp-|guten)print</driver>:<driver>gutenprint-ijs.5.0</driver>:' $f
done

# Fixed default paper tray for HP Business Inkjet 2800.
perl -p -i -e 's/(\*DefaultInputSlot:\s+)Auto/$1Tray1/' db/source/PPD/HP/business_inkjet/HP_Business_Inkjet_2800.ppd
# Fixed device ID lines in the HP PPDs
perl -p -i -e 's/1284DeviceId/1284DeviceID/' db/source/PPD/HP/*/*.ppd

%install
rm -rf %{buildroot}

# Do not use "make" macro, as parallelized build of Foomatic does not
# work.

# Install data files
make	PREFIX=%{_prefix} \
        DESTDIR=%buildroot \
        install

# Uncompress Perl script for cleaning up the PPD files
bzcat %{SOURCE2} > ./cleanppd.pl
chmod a+rx ./cleanppd.pl

# Do the clean-up
find %buildroot%{_datadir}/foomatic/db/source/PPD -name "*.ppd" -exec ./cleanppd.pl '{}' \;

# Remove PPDs which are not Adobe-compliant and therefore not working with
# CUPS 1.1.20 or newer
for ppd in `find %buildroot%{_datadir}/foomatic/db/source/PPD -name "*.ppd.gz"`
do
	cupstestppd -q $ppd || (
		rm -f $ppd && \
		echo "$ppd not Adobe-compliant. Deleted." && \
		echo $ppd >> deletedppds-%{name}-%{version}-%{release}.txt
	)
done

##### GENERAL STUFF

# Correct permissions
for f in %{buildroot}%{_datadir}/foomatic/db/source/*/*.xml; do
  chmod a-x $f
done
chmod a-x %{buildroot}%{_datadir}/foomatic/db/oldprinterids

##### SCRIPTS

# Restart the CUPS daemon when it is running, but do not start it when it
# is not running. The restart of the CUPS daemon updates the CUPS-internal
# PPD index

%post
/sbin/service cups condrestart > /dev/null 2>/dev/null || :

%postun
/sbin/service cups condrestart > /dev/null 2>/dev/null || :

##### CLEAN UP

%clean
rm -rf %{buildroot}

##### FILES

%files
%defattr(-,root,root)
%doc README USAGE COPYING
%_datadir/foomatic/db
%_datadir/cups/model/foomatic-db-ppds


%changelog
* Tue May 03 2011 Oden Eriksson <oeriksson@mandriva.com> 1:4.0-2.20110503.1mdv2011.0
+ Revision: 664404
- fix release
- 20110503
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 1:4.0-2.20101202.1mdv2011.0
+ Revision: 605910
- new snapshot (20101202)
- rebuild

* Fri Mar 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1:4.0-2.20100218.1mdv2010.1
+ Revision: 514479
- attempt to fix the build

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Update to latest snapshot

* Thu Oct 15 2009 Oden Eriksson <oeriksson@mandriva.com> 1:4.0-2.20091014.2mdv2010.0
+ Revision: 457604
- fix #54598 (foomatic-db conflicts with cups-drivers-foo2zjs)

* Wed Oct 14 2009 Oden Eriksson <oeriksson@mandriva.com> 1:4.0-2.20091014.1mdv2010.0
+ Revision: 457359
- 4.0-20091014

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 1:4.0-2.20090316.2mdv2010.0
+ Revision: 424463
- rebuild

* Mon Mar 16 2009 Frederik Himpe <fhimpe@mandriva.org> 1:4.0-2.20090316.1mdv2009.1
+ Revision: 355894
- Update to 20090316 snapshot

* Thu Feb 12 2009 Frederik Himpe <fhimpe@mandriva.org> 1:4.0-2.20090208.3mdv2009.1
+ Revision: 339899
- Update version in foo2zjs conflict, because of new conflicting files

* Mon Feb 09 2009 Frederik Himpe <fhimpe@mandriva.org> 1:4.0-2.20090208.2mdv2009.1
+ Revision: 338923
- Conflicts with older foo2zjs because of Generic-OAKT_Printer.xml file

* Sun Feb 08 2009 Frederik Himpe <fhimpe@mandriva.org> 1:4.0-2.20090208.1mdv2009.1
+ Revision: 338521
- Update to version 4.0 20090208 snapshot

* Sat Jan 03 2009 Frederik Himpe <fhimpe@mandriva.org> 1:3.0.2-2.20090103.1mdv2009.1
+ Revision: 323848
- Update to new version 20090103

* Mon Dec 29 2008 Oden Eriksson <oeriksson@mandriva.com> 1:3.0.2-2.20080810.2mdv2009.1
+ Revision: 321105
- rebuild

* Sun Aug 10 2008 Frederik Himpe <fhimpe@mandriva.org> 1:3.0.2-2.20080810.1mdv2009.0
+ Revision: 270332
- Update to new version 20080810

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 1:3.0.2-2.20080518.1mdv2009.0
+ Revision: 264478
- rebuild early 2009.0 package (before pixel changes)

* Sun May 18 2008 Frederik Himpe <fhimpe@mandriva.org> 1:3.0.2-1.20080518.1mdv2009.0
+ Revision: 208700
- New version
- Package COPYING, as not everything is under the GPLv2

  + Marcelo Ricardo Leitner <mrl@mandriva.com>
    - Make install script more readable.

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Dec 20 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 1:3.0.2-1.20071218.1mdv2008.1
+ Revision: 135852
- New upstream: 20071218

  + Thierry Vignaud <tv@mandriva.org>
    - fix description

* Mon Dec 17 2007 Thierry Vignaud <tv@mandriva.org> 1:3.0.2-1.20070820.2mdv2008.1
+ Revision: 125176
- kill re-definition of %%buildroot on Pixel's request

* Thu Sep 13 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 1:3.0.2-1.20070820.2mdv2008.0
+ Revision: 84994
- Do not require ghostscript and printer-filter packages. This package is just
  an informations database.
- Specfile cleanup.

* Thu Aug 30 2007 Marcelo Ricardo Leitner <mrl@mandriva.com> 1:3.0.2-1.20070820.1mdv2008.0
+ Revision: 75989
- New upstream: 20070820
- Removed conflicting files with other cups-drivers packages.

* Thu Jun 28 2007 Adam Williamson <awilliamson@mandriva.org> 1:3.0.2-1.20070627.1mdv2008.0
+ Revision: 45335
- new snapshot 20070627, clean spec, rebuild for 2008


* Mon Mar 19 2007 Thierry Vignaud <tvignaud@mandriva.com> 3.0.2-1.20060906.3mdv2007.1
+ Revision: 146587
- Import foomatic-db

* Mon Mar 19 2007 Thierry Vignaud <tvignaud@mandriva.com> 3.0.2-1.20060906.3mdv2007.1
- do not package big ChangeLog

* Thu Sep 07 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060906.2mdv2007.0
- Updated foomatic-db to later state of the 06/09/2006 (Fixed entry for
  Epson Stylus C65).

* Thu Sep 07 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060906.1mdv2007.0
- Updated foomatic-db to the state of the 06/09/2006 (Added new Samsung
  printers ML-1520, ML-1610, ML-1740, ML-2010, ML-2250).

* Sat Aug 19 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060818.1mdv2007.0
- Updated foomatic-db to the state of the 26/07/2006 (Added PPD files
  for new printers from Gestetner, Infotec, Lanier, NRG, Ricoh, Savin,
  and Okidata, added SiPix Pocket Printer A6).

* Thu Jul 27 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060726.1mdv2007.0
- Updated foomatic-db to the state of the 26/07/2006 (Added PPD files for
  new Sharp and Kyocera printers, added Kyocera FS-1016MFP).
- Fixed device ID lines in some HP PPDs.

* Mon Jul 03 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060630.1mdv2007.0
- Updated foomatic-db to the state of the 30/06/2006 (Added PPD file for
  Epson EPL-N2550 PostScript printer)

* Fri Jun 09 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060608.1mdv2007.0
- Updated foomatic-db to the state of the 08/06/2006 (Added auto-detection
  information for the Konica Minolta magicolor DL series printers, thanks
  to Sean Zhan from Konica Minolta).

* Thu Jun 08 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060607.1mdv2007.0
- Updated foomatic-db to the state of the 07/06/2006 (Unprintable margin
  definitions for the HP LaserJet 1022, added new HP inkjet printers, to be 
  supported with HPLIP 0.9.12: HP DeskJet D1300, D2300, D4100, PhotoSmart
  A430, A510, A610, A710, C3100, C4100, D7300).

* Wed Jun 07 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060606.1mdv2007.0
- Updated foomatic-db to the state of the 06/06/2006 (Updated "foo2zjs"
  and "foo2hp" driver data, added HP Color LaserJet 1600 and LaserJet 1018,
  updated HP LaserJet 1022 to use "foo2zjs" as default driver).

* Sat May 20 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060519.1mdk
- Updated foomatic-db to the state of the 19/05/2006 (Added Konica Minolta
  magicolor DL series, added new HP PostScript printers to "Postscript"
  driver entry, so that their PostScript PPDs appear in printer setup
  tools).

* Thu May 11 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060510.1mdk
- Updated foomatic-db to the state of the 10/05/2006 (Added HP Color
  LaserJet 2605, LaserJet 5200, 5200L, OfficeJet 4300, 6300, many printers
  from Ricoh and partners).

* Thu Mar 30 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060329.1mdk
- Updated foomatic-db to the state of the 29/03/2006 (Added Brother P-Touch
  label printers, updated data for Epson laser printer drivers "eplaser" and
  "eplase-jp", added Epson LP-S4500 and LP-S6500, fixed entry for HP
  DeskJet F300).

* Tue Mar 07 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060307.1mdk
- Updated foomatic-db to the state of the 07/03/2006 (HP Color LaserJet 2600
  and HP LaserJet 1020 now supported by "foo2zjs", HP DeskJet F300 added).
- Removed fixing "600x600x2dpi" resolutions in HP's PPDs, this is fixxed
  upstream now.

* Mon Feb 27 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060227.1mdk
- Updated foomatic-db to the state of the 27/02/2006 (Added ANSI paper
  sizes for large format printers).

* Sat Feb 25 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060225.1mdk
- Updated foomatic-db to the state of the 25/02/2006 (Added HP DesignJet
  100, 500, 800, 5000, updated HP DesignJet 5500).

* Fri Feb 24 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060224.1mdk
- Updated foomatic-db to the state of the 24/02/2006 (Printer entries for 
  all printers which are supported by Gutenprint).

* Thu Feb 23 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060223.1mdk
- Updated foomatic-db to the state of the 23/02/2006 (New PPD files from
  Ricoh: LockedPrint, UserCode, SamplePrint, DocumentServer also on
  the Ricoh, Gestetner, Infotec, Lanier, NRG, and Savin PostScript printers
  now).
- Removed source 3, merged upstream.

* Fri Feb 17 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060217.1mdk
- Updated foomatic-db to the state of the 17/02/2006 (New PPD files from
  Sharp and Kyocera, new HP printers, new Epson printers, fixes for HP
  DeskJet 520, ...).
- Fixed HP's PostScript PPDs: "600x600x2dpi" is not Adobe-spec-conforming,
  replaced it by "1200x600dpi".
- Fixed default paper tray in PostScript PPD for HP Business Inkjet 2800.

* Fri Jan 06 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060105.2mdk
- Fixed file conflict with printer-filters package
  (/usr/share/foomatic/db/source/driver/m2400w.xml).
- Introduced %%mkrel.

* Thu Jan 05 2006 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20060105.1mdk
- Updated foomatic-db to the state of the 05/01/2006 (Brother PostScript 
  PPD files; Minolta PagePro 1400, magicolor 2400W, HP Color LaserJet 
  3000, 3800; many new Ricoh and partners PPDs and Locked Print/user Code 
  support for PCL-XL printers from Ricoh and partners; bug fixes and new
  device IDs).

* Thu Oct 27 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20051026.1mdk
- Updated foomatic-db to the state of the 26/10/2005 (Moved
  manufacturer-supplied PPD files into the foomatic-db package).

* Fri Sep 02 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20050825.2mdk
- Added HP PSC 1510.

* Thu Aug 25 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20050825.1mdk
- Updated foomatic-db to the state of the 25/08/2005 (Fixed PPD file link
  for HP LaserJet 4250, separated broken "lj4dith" driver from "ljet4"
  driver).

* Tue Aug 16 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20050816.1mdk
- Updated foomatic-db to the state of the 16/08/2005 (Fix in paper tray
  selection for PCL-6/XL drivers).

* Wed Aug 03 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20050802.1mdk
- Updated foomatic-db to the state of the 02/08/2005 (Tons of new printer
  models after LE 2005, a lot of new auto-detection data from Red Hat,
  Well-Tempered Screening for black-and-white laser printer GhostScript
  drivers, bug fixes).

* Mon May 30 2005 Till Kamppeter <till@mandriva.com> 1:3.0.2-1.20050529.1mdk
- Updated foomatic-db to the state of the 29/05/2005 (Added Epson Stylus
  Photo R1800; updates for Gutenprint 5.0.x; many smaller bug fixes, 
  mainly from Red Hat).

* Thu May 19 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050518.1mdk
- Updated foomatic-db to the state of the 18/05/2005 (Updates for HPLIP 
  0.9.3/HPIJS 2.1.3; many smaller bug fixes, mainly from Red Hat).

* Tue Apr 05 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050404.1mdk
- Updated foomatic-db to the state of the 04/04/2005 (New printers: HP 
  DesignJet 500ps, HP DesignJet 100plus, HP LaserJet 4240, HP LaserJet 9040,
  HP Color LaserJet 4610, HP LaserJet 1022, HP Business Inkjet 1000; updates
  for HPLIP 0.9.1/HPIJS 2.1.1; "Resolution" option for "dnj650c" driver).

* Thu Mar 31 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050330.1mdk
- Updated foomatic-db to the state of the 30/03/2005 (New printers: HP
  Color LaserJet 35xx, Lexmark Optra E321 (bug 15026); HP LaserJet 101x 
  now used with HPIJS driver, tray selection foe Generic and Lexmark
  PostScript printers (bug 15055), updates for HPLIP 0.9/HPIJS 2.1).

* Thu Mar 17 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050318.1mdk
- Updated foomatic-db to the state of the 18/03/2005 (New printers: HP
  DskJet 6600, 9800).

* Fri Mar 04 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050304.1mdk
- Updated foomatic-db to the state of the 04/03/2005 (Added 162 new printer
  entries contributed by Ricoh: PostScript printers of the brands
  Ricoh, Lanier, Infotec, Gestetner, Savin, NRG).

* Thu Mar 03 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050303.1mdk
- Updated foomatic-db to the state of the 03/03/2005 (Added 33 new Epson
  laser printers: Japanese Epson LP series, Epson AcuLaser C9100; renamed
  driver entry "epkowa-laser" to "eplaser", new driver entry "eplaser-jp").

* Fri Feb 25 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050225.1mdk
- Updated foomatic-db to the state of the 25/02/2005 (Corrected recommended
  driver for printers to be used with the "lxm3200-tweaked" driver).

* Thu Feb 24 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050224.1mdk
- Updated foomatic-db to the state of the 24/02/2005 (Added support
  for the "oki4w" GhostScript driver for Okidata Okipage 4W and
  compatible printers).

* Tue Feb 22 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050222.2mdk
- Updated foomatic-db from CVS again (fixes for the new Ricoh entries).

* Tue Feb 22 2005 Till Kamppeter <till@mandrakesoft.com> 1:3.0.2-1.20050222.1mdk
- Updated foomatic-db to the state of the 22/02/2005 (Added printer
  entries contributed by Ricoh: PostScript printers of the brands
  Ricoh, Lanier, Infotec, Gestetner, Savin, NRG, fixed PPD files
  generated by the "Postscript" driver, they failed "cupstestppd" due
  to the "NotCapable" choice in the "Duplex" option).
- Let version number contain the version of Foomatic again.

* Sat Feb 12 2005 Till Kamppeter <till@mandrakesoft.com> 20050212-2mdk
- Fixed entry for HP DeskJet 6540.

* Fri Feb 11 2005 Till Kamppeter <till@mandrakesoft.com> 20050211-1mdk
- Updated foomatic-db to the state of the 12/02/2005 (full support
  for HP LaserJet 1010/1012 and more).
- Removed Foomatic files for drivers which have their own Foomatic data.

* Thu Feb 10 2005 Till Kamppeter <till@mandrakesoft.com> 20050128-4mdk
- Corrected Gimp-Print as recommended driver, must be "gimp-print-ijs".

* Tue Feb 08 2005 Till Kamppeter <till@mandrakesoft.com> 20050128-3mdk
- Removed the call of "foomatic-preferred-driver".

* Fri Feb 04 2005 Till Kamppeter <till@mandrakesoft.com> 20050128-2mdk
- Added "BuildRequires: foomatic-db-engine".

* Fri Jan 28 2005 Till Kamppeter <till@mandrakesoft.com> 20050128-1mdk
- Updated foomatic-db to the state of the 28/01/2005.

