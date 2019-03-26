Name:           log4cpp
#Version:        1.1.4
Release:        1%{?dist}
Summary:        C++ logging library

Group:          Development/Libraries
License:        LGPLv2+
URL:            http://sourceforge.net/projects/log4cpp/
Source0:        http://downloads.sourceforge.net/log4cpp/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  doxygen
BuildRequires:  automake, autoconf, libtool

%description
A library of C++ classes for flexible logging to files, syslog, IDSA and
other destinations. It is modeled after the Log for Java library
(http://www.log4j.org), staying as close to their API as is reasonable.

%package devel
Summary:        Header files, libraries and development man pages  %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}
%if 0%{?el4}%{?el5}
Requires:       pkgconfig
%endif

%description devel
This package contains the header files, static libraries and development
man pages for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%package doc
Summary:        Development documentation for %{name}
Group:          Development/Libraries
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description doc
This package contains the development documentation for %{name}.
If you like to documentation to develop programs using %{name},
you will need to install %{name}-devel.

%prep
%setup
#%patch0 -p1

#Convert line endings.
iconv -f iso8859-1 -t utf-8 ChangeLog > ChangeLog.conv && mv -f ChangeLog.conv ChangeLog

%build
autoconf
%configure
make %{?_smp_mflags}

%install

#%make_install DESTDIR=%{buildroot}
cd src && %make_install DESTDIR=%{buildroot}
cd ../include && %make_install DESTDIR=%{buildroot}
cd ..
mkdir -p  %{buildroot}/%{_docdir}/log4cpp-%{version}
cp -rf doc/html %{buildroot}/%{_docdir}/log4cpp-%{version}
rm %{buildroot}/%{_docdir}/log4cpp-%{version}/html/Makefile*
mkdir -p %{buildroot}/%{_bindir}  %{buildroot}/%{_libdir}/pkgconfig %{buildroot}/%{_datadir}/aclocal
mkdir -p %{buildroot}/%{_mandir}
cp -r doc/man/man3 %{buildroot}/%{_mandir}/
install -m 755 log4cpp-config %{buildroot}/%{_bindir}/log4cpp-config
cp log4cpp.pc %{buildroot}/%{_libdir}/pkgconfig/log4cpp.pc
cp log4cpp.m4 %{buildroot}/%{_datadir}/aclocal/log4cpp.m4
cp log4cpp.cfg %{buildroot}/%{_docdir}/log4cpp-%{version}/log4cpp.cfg
#cp src/.libs/*.so %{buildroot}/%{_libdir}
#cp src/.libs/*.a %{buildroot}/%{_libdir}
#cp -r %{buildroot}/%{_includedir}/log4cpp %{buildroot}/%{_includedir}
#cp -r %{buildroot}/
#rm -f %{buildroot}%{_libdir}/*.a
rm -f %{buildroot}%{_libdir}/*.la

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root, 0755)
%{_libdir}/liblog4cpp.so.*
%doc ChangeLog COPYING

%files devel
%{_bindir}/log4cpp-config
%{_includedir}/log4cpp/
%{_libdir}/liblog4cpp.so
%{_libdir}/liblog4cpp.a
%{_libdir}/pkgconfig/log4cpp.pc
%{_datadir}/aclocal/log4cpp.m4
%{_docdir}/log4cpp-%{version}/log4cpp.cfg
%{_mandir}/man3

%files doc
%doc %{_docdir}/log4cpp-%{version}/html

%changelog
