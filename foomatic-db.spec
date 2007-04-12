%define version 3.0.2
%define releasedate 20060906
%define release %mkrel 1.%{releasedate}.3

##### RPM PROBLEM WORKAROUNDS

# Suppress automatically generated Requires for Perl libraries.
#define _requires_exceptions perl\(.*\)

#define _unpackaged_files_terminate_build       0 
#define _missing_doc_files_terminate_build      0

##### GENERAL DEFINITIONS

Name:		foomatic-db
Version:	%{version}
Release:	%{release}
Epoch:		1
Summary:        Foomatic printer/driver database
License:        GPL
Group:          System/Servers
Url:            http://www.linuxprinting.org/
Requires:       ghostscript, printer-filters, foomatic-db-engine
Conflicts:	postscript-ppds <= 2006-1mdk
BuildArchitectures: noarch

##### BUILDREQUIRES

BuildRequires:	autoconf2.5 automake foomatic-db-engine cups cups-common

##### FOOMATIC SOURCES

# Foomatic packages
Source:		http://www.linuxprinting.org/download/foomatic/%{name}-%{releasedate}.tar.bz2

# Temporarily added the HP PSC 1510.
#Source1:	HP-PSC_1510.xml.bz2

# Perl script to clean up Manufacturer entries in the PPD files, so that
# drivers are sorted by the printer manufacturer in the graphical frontends
Source2:	cleanppd.pl.bz2



##### BUILD ROOT

BuildRoot:	%_tmppath/%name-%version-%release-root



##### PACKAGE DESCRIPTIONS

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
 
The site http://www.linuxprinting.org/ is based on this database.

This package is the Foomatic database, an XML database containing
information about the capabilities of near 1000 printers and around
250 drivers. Especially it contains the information how and with which
options the drivers have to be executed.


%prep
# remove old directory
rm -rf $RPM_BUILD_DIR/%{name}-[0-9]*
mkdir $RPM_BUILD_DIR/%{name}-%{releasedate}

##### FOOMATIC

# Source trees for installation
%setup -q -n %{name}-%{releasedate}
#bzcat %{SOURCE1} > db/source/printer/HP-PSC_1510.xml

%build

cd $RPM_BUILD_DIR/%{name}-%{releasedate}

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


# Delete drivers with empty command line prototype, they would give
# unusable printer/driver combos.
FOOMATICDB=`pwd` %{_sbindir}/foomatic-cleanupdrivers

# Correct the default drivers of the printer entries to have a valid
# default for every printer.
#FOOMATICDB=`pwd` %{_sbindir}/foomatic-preferred-driver

# Correct recommended driver "gimp-print" or "gutenprint", must be 
# "gutenprint-ijs.5.0".
for f in db/source/printer/*.xml; do
	perl -p -i -e 's:<driver>(gimp-|guten)print</driver>:<driver>gutenprint-ijs.5.0</driver>:' $f
done

# Fix HP's PostScript PPDs: "600x600x2dpi" is not Adobe-spec-conforming,
# replace it by "1200x600dpi".
#perl -p -i -e 's/600x600x2dpi/1200x600dpi/' db/source/PPD/*/*/*.ppd

# Fixed default paper tray for HP Business Inkjet 2800.
perl -p -i -e 's/(\*DefaultInputSlot:\s+)Auto/$1Tray1/' db/source/PPD/HP/business_inkjet/HP_Business_Inkjet_2800.ppd
# Fixed device ID lines in the HP PPDs
perl -p -i -e 's/1284DeviceId/1284DeviceID/' db/source/PPD/HP/*/*.ppd

%install

cd $RPM_BUILD_DIR/%{name}-%{releasedate}

rm -rf %{buildroot}

# Do not use "make" macro, as parallelized build of Foomatic does not
# work.

# Install data files
make	PREFIX=%{_prefix} \
        DESTDIR=%buildroot \
        install

# Install documentation
install -d %buildroot%{_docdir}/foomatic-db-%{version}
cp README USAGE TODO \
	%buildroot%{_docdir}/foomatic-db-%{version}

# Uncompress Perl script for cleaning up the PPD files
bzcat %{SOURCE2} > ./cleanppd.pl
chmod a+rx ./cleanppd.pl

# Do the clean-up
find %buildroot%{_datadir}/foomatic/db/source/PPD -name "*.ppd" -exec ./cleanppd.pl '{}' \;

# Remove PPDs which are not Adobe-compliant and therefore not working with
# CUPS 1.1.20 or newer
for ppd in `find %buildroot%{_datadir}/foomatic/db/source/PPD -name "*.ppd.gz" -print`; do cupstestppd -q $ppd || (rm -f $ppd && echo "$ppd not Adobe-compliant. Deleted." && echo $ppd >> deletedppds-%{name}-%{version}-%{release}.txt); done



##### GENERAL STUFF

# Correct permissions for all documentation files
chmod -R a+rX %{buildroot}%{_docdir}
chmod -R a-x %{buildroot}%{_docdir}/*/*
chmod -R go-w %{buildroot}%{_docdir}
chmod -R u+w %{buildroot}%{_docdir}
for f in %{buildroot}%{_datadir}/foomatic/db/source/*/*.xml; do
  chmod a-x $f
done
chmod a-x %{buildroot}%{_datadir}/foomatic/db/oldprinterids



##### FILES

%files -n foomatic-db
%defattr(-,root,root)
%docdir %{_docdir}/foomatic-db-%{version}
%{_docdir}/foomatic-db-%{version}
%_datadir/foomatic/db
%_datadir/cups/model/foomatic-db-ppds



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


