%define glib2_version 2.6.0
%define pango_version 1.8.0
%define gtk2_version 2.6.0
%define libgnomeui_version 2.6.0
%define libgnomeprint_version 2.2.0
%define libgnomeprintui_version 2.2.0
%define desktop_file_utils_version 0.9
%define nautilus_version 2.22.1
%define gnome_doc_utils_version 0.3.2

Summary:	Tool for viewing and creating archives
Name:		file-roller
Version:	2.28.2
Release: 	6%{?dist}
License:	GPLv2+
Group:		Applications/Archiving
URL:		http://download.gnome.org/sources/file-roller/
Source:		http://download.gnome.org/sources/file-roller/2.28/file-roller-%{version}.tar.bz2

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: glib2-devel >= %{glib2_version}
BuildRequires: pango-devel >= %{pango_version}
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: libglade2-devel
BuildRequires: nautilus-devel >= %{nautilus_version}
BuildRequires: libtool
BuildRequires: gettext
BuildRequires: libSM-devel
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: gnome-doc-utils >= %{gnome_doc_utils_version}
BuildRequires: GConf2-devel
BuildRequires: scrollkeeper
BuildRequires: intltool

Requires(post): scrollkeeper
Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2

Requires(postun): scrollkeeper

Requires: GConf2

# The context menu API changed in 2.2.0:
Conflicts: nautilus < 2.2.0

# upstream fix
Patch0: file-roller-arj-crash.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=552194
Patch1: fileroller-translations.patch
Patch2: fileroller-translations2.patch

# Crash extracting to gvfs folder with drag and drop
# https://bugzilla.redhat.com/show_bug.cgi?id=590266
# http://bugzilla.gnome.org/show_bug.cgi?id=617769
Patch3: file-roller-2.28.2-gvfs-fuse.patch

# upstream fix
# https://bugzilla.redhat.com/show_bug.cgi?id=589550
Patch4: file-roller-fix7z.patch

%description
File Roller is an application for creating and viewing archives files,
such as tar or zip files.

%prep
%setup -q
%patch0 -p1 -b .arj-crash
%patch1 -p1 -b .translations
%patch2 -p2 -b .translations2
%patch3 -p1 -b .gvfs-fuse
%patch4 -p1 -b .fix7z

%build
%configure --disable-scrollkeeper --disable-static
export tagname=CC
make LIBTOOL=/usr/bin/libtool

%install
rm -rf $RPM_BUILD_ROOT

export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
export tagname=CC
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor gnome --delete-original       \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications             \
  --remove-only-show-in=GNOME                               \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

rm -f $RPM_BUILD_ROOT%{_libdir}/nautilus/extensions-2.0/*.{a,la}

rm -f $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/icon-theme.cache

%find_lang %{name} --with-gnome

%clean
rm -rf $RPM_BUILD_ROOT

%post
update-desktop-database &> /dev/null || :
scrollkeeper-update -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
	%{_sysconfdir}/gconf/schemas/file-roller.schemas 2>&1 >/dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule \
	%{_sysconfdir}/gconf/schemas/file-roller.schemas 2>&1 >/dev/null
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule \
	%{_sysconfdir}/gconf/schemas/file-roller.schemas 2>&1 >/dev/null
fi

%postun
update-desktop-database &> /dev/null || :
scrollkeeper-update -q
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%files -f %{name}.lang
%defattr(-, root, root)
%doc README COPYING NEWS AUTHORS
%{_bindir}/file-roller
%{_datadir}/file-roller
%{_datadir}/applications/gnome-file-roller.desktop
%{_sysconfdir}/gconf/schemas/file-roller.schemas
%{_libdir}/nautilus/extensions-2.0/libnautilus-fileroller.so
%{_libexecdir}/file-roller
%{_datadir}/icons/hicolor/*/apps/file-roller.png
%{_datadir}/icons/hicolor/scalable/apps/file-roller.svg

%changelog
* Thu Aug  5 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-6
- Update translations
Resolves: #552194

* Mon May 24 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-5
- Fix a possible crash
Resolves: #589550

* Tue May 18 2010 Tomas Bzatek <tbzatek@redhat.com> 2.28.2-4
- Fix archive handling on remote GIO mounts without running fuse daemon (#590266)

* Wed May  5 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-3
- Update translations
Resolves: #552194

* Tue Jan 12 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-2
- Fix a crash in the arj loader

* Mon Jan  4 2010 Matthias Clasen <mclasen@redhat.com> 2.28.2-1
- Update to 2.28.2, sync with Fedora 12
- Drop upstreamed patches

* Mon Dec 14 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-4
- Add forgotten patch

* Mon Dec 14 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-3
- Fix a wrong use of gdk_property_get

* Thu Oct 29 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-2
- Fix sticky DND

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> 2.28.1-1
- Update to 2.28.1

* Thu Oct  1 2009 Matthias Clasen <mclasen@redhat.com> 2.28.0-2
- Respect button-images setting

* Mon Sep 21 2009 Matthias Clasen <mclasen@redhat.com> 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> 2.27.92-1
- Update to 2.27.92

* Mon Aug 24 2009 Matthias Clasen <mclasen@redhat.com> 2.27.91-1
- Update to 2.27.91

* Fri Aug 14 2009 Matthias Clasen <mclasen@redhat.com> 2.27.90-2
- Make opening .cab files work

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> 2.27.90-1
- Update to 2.27.90

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> 2.27.3-1
- Update to 2.27.3

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.27.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 Matthias Clasen <mclasen@redhat.com> 2.27.2-1
- Update to 2.27.2

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> 2.27.1-1
- Update to 2.27.1

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/file-roller/2.26/file-roller-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> 2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> 2.25.92-1
- Update to 2.25.92

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Tue Jan 20 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.2-1
- Update to 2.25.2

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.1-5
- Update to 2.25.1
- Clean up BRs

* Sun Nov 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-2
- Shorten summary 

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.6-1
- Update to 2.23.6
- Drop upstreamed patches

* Fri Aug  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-3
- Fix a segfault

* Fri Aug  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-2
- Fix the folder icons

* Mon Aug  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.4-1
- Update to 2.23.4

* Fri Jul 11 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-2
- Fix icon lookup 

* Wed Jun 18 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Tue Jun  3 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2-1
- Update to 2.23.2

* Thu Apr 24 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-1
- Update to 2.23.1

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Fri Apr  4 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-2
- Update the gio patch

* Tue Mar 11 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Tue Mar 11 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-3
- Port nautilus extension to gio

* Thu Mar  6 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-2
- Don't OnlyShowIn=GNOME

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Tue Feb 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Tue Jan 08 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.1-1
- Update to 2.21.1
- Remove obsolete patch

* Sun Dec 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.2-2
- Rebuild nautilus extension against nautilus 2.21

* Mon Nov 26 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.2-1
- Update to 2.20.2 (translation updates)

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (crash fix)

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Mon Sep  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Mon Sep  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.91-1
- Update to 2.19.91

* Fri Aug 24 2007 Adam Jackson <ajax@redhat.com> - 2.19.90-2
- Rebuild for build ID

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90

* Mon Aug  6 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-3
- Use %%find_lang for help files

* Thu Aug  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-2
- Update the license field

* Mon Jul 30 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.4-1
- Update to 2.19.4

* Tue Jun 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3

* Mon Jun  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-1
- Update to 2.19.1

* Thu Apr 12 2007 Christopher Aillon <caillon@redhat.com> - 2.18.1-1
- Update to 2.18.1

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92

* Mon Feb 12 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.91-1
- Update to 2.17.91

* Mon Feb  5 2007 Christopher Aillon <caillon@redhat.com> - 2.17.90-2
- Packaging issues:
  Remove unneeded desktop-file-utils requires
  Build with --disable-static

* Mon Jan 22 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.90-1
- Update to 2.17.90

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.4-1
- Update to 2.17.4

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.3-1
- Update to 2.17.3

* Tue Nov  7 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Sat Oct 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.1-1
- Update to 2.17.1

* Fri Sep  8 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-2
- Fix directory ownership issues

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0
- Add missing BRs

* Tue Aug 22 2006 Matthias Clasen <mclasen@rehdat.com> - 2.15.93-2.fc6
- Add a %%preun script
- Silence %%post and %%preun

* Mon Aug 21 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.93-1.fc6
- Update to 2.15.93

* Sat Aug 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.92-1.fc6
- Update to 2.15.92
- BR nautilus-devel

* Thu Aug  3 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.90-1.fc6
- Update to 2.15.90

* Sun Jul 30 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-2
- Avoid warnings from recent menu

* Wed Jul 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.1-1
- Update to 2.15.1

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.14.3-4.1
- rebuild

* Thu Jun  8 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.3-4 
- Add more BuildRequires

* Mon Jun  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.3-3
- Rebuild

* Mon May 29 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.3-2
- Update to 2.14.3

* Tue Apr 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.2-3
- Remove dot from summary

* Tue Apr 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.2-2
- Update to 2.14.2
- Some .spec file cleanups

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Mon Mar 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Mon Feb 27 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.92-1
- Update to 2.13.92

* Tue Feb 21 2006 Karsten Hopp <karsten@redhat.de> 2.13.91-2
- BuildRequire: gnome-doc-utils

* Wed Feb 15 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.91-1
- Update to 2.13.91

* Sun Feb 12 2006 Christopher Aillon <caillon@redhat.com> 2.13.90-2
- Rebuild

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> 2.13.90-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 31 2006 Matthias Clasen <mclasen@redhat.com> 2.13.90-1
- Update to 2.13.90

* Tue Jan 16 2006 Matthias Clasen <mclasen@redhat.com> 2.13.4-1
- Update to 2.13.4

* Thu Jan 03 2006 Matthias Clasen <mclasen@redhat.com> 2.13.3-1
- Update to 2.13.3

* Thu Dec 14 2005 Matthias Clasen <mclasen@redhat.com> 2.13.2-1
- Update to 2.13.2
- Remove upstreamed patches

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  1 2005 Matthias Clasen <mclasen@redhat.com> 2.13.1-1
- Update to 2.13.1

* Thu Nov  3 2005 Christopher Aillon <caillon@redhat.com> 2.12.1-2
- Add 7-zip to the desktop file, since file-roller supports it

* Thu Oct  6 2005 Matthias Clasen <mclasen@redhat.com> 2.12.1-1
- Update to 2.12.1

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 2.12.0-1
- Update to 2.12.0

* Wed Aug 17 2005 David Zeuthen <davidz@redhat.com> 
- Disable scrollkeeper until gnome-doc changes are sorted out

* Tue Aug 16 2005 Matthias Clasen <mclasen@redhat.com> 
- New upstream version

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-1
- New upstream version

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> 2.11.2-1
- New upstream version

* Fri Mar 18 2005 David Zeuthen <davidz@redhat.com> 2.10.0-1
- New upstream version

* Thu Mar  3 2005 Marco Pesenti Gritti <mpg@redhat.com> 2.9.92-1
- Update to 2.9.92

* Wed Feb  9 2005 Matthias Clasen <mclasen@redhat.com> 2.9.91-1
- Update to 2.9.91

* Mon Jan 31 2005 Matthias Clasen <mclasen@redhat.com> 2.9.4-1
- Update to 2.9.4

* Wed Nov  3 2004 Christopher Aillon <caillon@redhat.com> 2.8.3-1
- Update to 2.8.3

* Wed Oct 13 2004 Christopher Aillon <caillon@redhat.com> 2.8.2-2
- Update to 2.8.2

* Tue Oct  5 2004 Christopher Aillon <caillon@redhat.com> 2.8.1-1
- Update to 2.8.1

* Thu Sep 30 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-4
- Prereq desktop-file-utils >= 0.9

* Tue Sep 28 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-2
- update-desktop-database after uninstall.
- nautilus shouldn't try to open remote files with file-roller (#133592)

* Wed Sep 22 2004 Christopher Aillon <caillon@redhat.com> 2.8.0-1
- Update to 2.8.0

* Mon Aug 30 2004 Christopher Aillon <caillon@redhat.com> 2.7.5-0
- Update to 2.7.5

* Wed Aug 18 2004 Christopher Aillon <caillon@redhat.com> 2.7.4-0
- Update to 2.7.4

* Mon Aug 16 2004 Christopher Aillon <caillon@redhat.com> 2.7.3-3
- Use update-desktop-database instead of rebuild-mime-info-cache

* Sun Aug 15 2004 Christopher Aillon <caillon@redhat.com> 2.7.3-2
- Rebuild MIME info cache

* Thu Aug 05 2004 Christopher Aillon <caillon@redhat.com> 2.7.3-1
- Update to 2.7.3

* Sat Jul 03 2004 Christopher Aillon <caillon@redhat.com> 2.6.2-1
- update to 2.6.2

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun 09 2004 Christopher Aillon <caillon@redhat.com> 2.6.1-1
- update to 2.6.1

* Fri Apr  2 2004 Alex Larsson <alexl@redhat.com> 2.6.0-1
- update to 2.6.0

* Tue Mar  9 2004 Alexander Larsson <alexl@redhat.com> 2.5.6-1
- update to 2.5.6

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Alexander Larsson <alexl@redhat.com> 2.5.5-1
- update to 2.5.5

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jan 30 2004 Alexander Larsson <alexl@redhat.com> 2.5.2-1
- update to 2.5.2

* Fri Oct  3 2003 Alexander Larsson <alexl@redhat.com> 2.4.0.1-1
- 2.4.0.1

* Tue Aug 19 2003 Alexander Larsson <alexl@redhat.com> 2.3.4-1
- update for gnome 2.3

* Fri Aug  8 2003 Elliot Lee <sopwith@redhat.com> 2.2.3-5
- Fix libtool

* Wed Jul  9 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-4.E
- Rebuild

* Thu Jun 5 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jun  5 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-3
- Update scrollkeeper prereq to version 0.3.4-2 (#92251)

* Mon May 19 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-2
- Use system libtool

* Mon May 19 2003 Alexander Larsson <alexl@redhat.com> 2.2.3-1
- Update to 2.2.3

* Tue Feb  4 2003 Alexander Larsson <alexl@redhat.com> 2.2.1-2
- Add patch that disables monitoring in recent-files

* Fri Jan 31 2003 Alexander Larsson <alexl@redhat.com> 2.2.1-1
- Update to 2.2.1, more translations

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Jan 21 2003 Alexander Larsson <alexl@redhat.com> 2.2.0-1
- Update to 2.2.0
- Conflict with nautilus < 2.2.0

* Thu Jan  9 2003 Alexander Larsson <alexl@redhat.com> 2.1.5-1
- Update to 2.1.5

* Thu Dec 19 2002 Havoc Pennington <hp@redhat.com>
- 2.1.4
- remove noscripts patch, now upstream

* Mon Dec  9 2002 Alexander Larsson <alexl@redhat.com> 2.1.3-3
- fix server file path

* Mon Dec  9 2002 Alexander Larsson <alexl@redhat.com> 2.1.3-2
- Remove unpackaged files

* Mon Dec  9 2002 Alexander Larsson <alexl@redhat.com> 2.1.3-1
- Update to 2.1.3

* Fri Dec  6 2002 Havoc Pennington <hp@redhat.com>
- 2.1.2
- fix unpackaged files

* Wed Jul 31 2002 Havoc Pennington <hp@redhat.com>
- fix URL field
- put icon in file list
- 2.0.0 stable release

* Fri Jun 21 2002 Havoc Pennington <hp@redhat.com>
- initial build

