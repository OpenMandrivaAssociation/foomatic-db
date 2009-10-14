%define version 4.0
%define releasedate 20091014
%define release %mkrel 2.%{releasedate}.1

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
Requires:	foomatic-db-engine
Conflicts:	postscript-ppds <= 2006-1mdk
Conflicts:	cups-drivers-foo2zjs < 0.0-0.20090122.2
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
