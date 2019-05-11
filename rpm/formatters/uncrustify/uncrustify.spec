Name:		uncrustify
Version:	%{vers}
Release:	%{rel}%{?dist}
Summary:	Reformat Source

License:	GPLv2
URL:		http://uncrustify.sourceforge.net/
Source0:	%{name}-%{version}.%{rel}.tbz
BuildRequires:	gcc gcc-c++ libstdc++ cmake

%description
Source Code Beautifier for C, C++, C#, D, Java, and Pawn

%prep
%autosetup -n %{name}

%build
mkdir build && cd build
%cmake ..
make %{?_smp_mflags}


%install
cd build
make install DESTDIR=$RPM_BUILD_ROOT


%files
%doc COPYING AUTHORS NEWS README.md
%doc documentation
%{_bindir}/uncrustify
%{_mandir}/man1/uncrustify.1*


%changelog
* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.68.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 03 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 0.68.1-1
- Update to 0.68.1

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.66.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.66.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Jan  5 2018 Neal Becker <nbecker@nbecker2> - 0.66.1-1
- Update to 0.66.1

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.64-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.64-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.64-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Oct 15 2016 Michael Catanzaro <mcatanzaro@gnome.org> - 0.64-1
- Update to 0.64

* Sat Mar 26 2016 Michael Catanzaro <mcatanzaro@gnome.org> - 0.62-1
- Update to 0.62

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.60-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.60-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 0.60-8
- Rebuilt for GCC 5 C++11 ABI change

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.60-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.60-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 17 2014 Filipe Rosset <rosset.filipe@gmail.com> - 0.60-5
- Rebuilt to fix rhbz #926678 + spec cleanup

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.60-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.60-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jan 12 2013 Neal Becker <ndbecker2@gmail.com> - 0.60-2
- Update to 0.60
- Remove patch

* Mon Jul 23 2012 Ralf Corsépius <corsepiu@fedoraproject.org> - 0.58-4
- Append --disable-silent-rules to %%configure (Make building verbose).
- Add uncrustify-0.58.patch (Add missing include).
- Remove BR: autoconf.
- Modernize spec.

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.58-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.58-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri May 20 2011 Neal Becker <ndbecker2@gmail.com> - 0.58-1
- Update to 0.58

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.56-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon May 24 2010 Neal Becker <ndbecker2@gmail.com> - 0.56-2
- Remove 'BUGS'

* Mon May 24 2010 Neal Becker <ndbecker2@gmail.com> - 0.56-1
- Update to 0.56

* Sat Oct 17 2009 Neal Becker <ndbecker2@gmail.com> - 0.54-1
- Update to 0.54

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.52-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Mar  8 2009 Neal Becker <ndbecker2@gmail.com> - 0.52-1
- Update to 0.52

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.50-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Nov  3 2008 Neal Becker <ndbecker2@gmail.com> - 0.50-2
- Documentation fixes

* Mon Nov  3 2008 Neal Becker <ndbecker2@gmail.com> - 0.50-1
- Update to 0.50

* Sun Jun 15 2008 Neal Becker <ndbecker2@gmail.com> - 0.47-1
- Update to 0.47

* Thu Apr 24 2008 Neal Becker <ndbecker2@gmail.com> - 0.46-1
- Update to 0.46

* Sun Mar  9 2008 Neal Becker <ndbecker2@gmail.com> - 0.45-1
- Update to 0.45

* Wed Feb 13 2008 Neal Becker <ndbecker2@gmail.com> - 0.44-1
- Update to 0.44

* Tue Jan 29 2008 Neal Becker <ndbecker2@gmail.com> - 0.43-2
- Remove explicit dep libstdc++

* Tue Jan 29 2008 Neal Becker <ndbecker2@gmail.com> - 0.43-1
- Update to 0.43

* Sun Nov 18 2007 Neal Becker <ndbecker2@gmail.com> - 0.41-1
- Update to 0.41

* Tue Nov  6 2007 Neal Becker <ndbecker2@gmail.com> - 0.40-2
- Increase release tag to satisfy cvs
- Bump tag

* Tue Nov  6 2007 Neal Becker <ndbecker2@gmail.com> - 0.40-1
- Update to 0.40

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 0.35-2
- Rebuild for selinux ppc32 issue.

* Fri Jul 20 2007 Neal Becker <ndbecker2@gmail.com> - 0.35-1
- 0.35

* Tue Jun 12 2007 Neal Becker <ndbecker2@gmail.com> - 0.34-1
- bump to 0.34

