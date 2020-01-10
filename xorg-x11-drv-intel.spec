%define moduledir %(pkg-config xorg-server --variable=moduledir )
%define driverdir	%{moduledir}/drivers
%define gputoolsdate 20130625
#define gitdate 20120718
#define gitrev .%{gitdate}

%if 0%{?rhel} == 7
%define rhel7 1
%endif
%if 0%{?rhel} == 6
%define rhel6 1
%endif

Summary:   Xorg X11 Intel video driver
Name:      xorg-x11-drv-intel
Version:   2.99.911
Release:   8%{?gitrev}%{?dist}
URL:       http://www.x.org
License:   MIT
Group:     User Interface/X Hardware Support

%if 0%{?gitdate}
Source0:    xf86-video-intel-%{gitdate}.tar.bz2
%else
Source0:    http://xorg.freedesktop.org/archive/individual/driver/xf86-video-intel-%{version}.tar.bz2 
%endif
Source1:    make-intel-gpu-tools-snapshot.sh
Source3:    intel-gpu-tools-%{gputoolsdate}.tar.bz2
Source4:    make-git-snapshot.sh

Patch20: 0001-uxa-fix-pending.patch
Patch21: 0002-uxa-mst-support.patch
Patch23: redhat-intel-crtc-dpms.patch
Patch24: rhel6-uxa.patch
Patch25: 0001-configure-Don-t-link-the-driver-against-libX11.patch
Patch26: 0001-sna-gen8-Clamp-URB-allocations-for-GT3.patch
Patch100: igt-old-cairo.patch

ExclusiveArch: %{ix86} x86_64 ia64

BuildRequires: autoconf automake libtool
BuildRequires: xorg-x11-server-devel >= 1.10.99.902
BuildRequires: libXvMC-devel
BuildRequires: mesa-libGL-devel >= 6.5-9
BuildRequires: libdrm-devel >= 2.4.37
BuildRequires: libudev-devel
BuildRequires: libxcb-devel >= 1.5 
BuildRequires: xcb-util-devel
BuildRequires: cairo-devel
BuildRequires: glib2-devel

Requires:  kernel >= 2.6.32-33.el6
Requires:  libdrm >= 2.4.37
Requires: Xorg %(xserver-sdk-abi-requires ansic)
Requires: Xorg %(xserver-sdk-abi-requires videodrv)

%description 
X.Org X11 Intel video driver.

%package devel
Summary:   Xorg X11 Intel video driver XvMC development package
Group:     Development/System
Requires:  %{name} = %{version}-%{release}
Provides:  xorg-x11-drv-intel-devel = %{version}-%{release}

%description devel
X.Org X11 Intel video driver XvMC development package.

%package -n intel-gpu-tools
Summary:    Debugging tools for Intel graphics chips
Group:	    Development/Tools
Requires:   libxcb >= 1.5
Requires:   xcb-util

%description -n intel-gpu-tools
Debugging tools for Intel graphics chips

%if 0%{?gitdate}
%define dirsuffix %{gitdate}
%else
%define dirsuffix %{version}
%endif

%prep
%setup -q -n xf86-video-intel-%{?gitdate:%{gitdate}}%{!?gitdate:%{dirsuffix}} -b3
%patch20 -p1 -b .uxa-fix
%patch21 -p1 -b .mst
#patch23 -p1 -b .lid-hack
%patch24 -p1 -b .uxa
%patch25 -p1 -b .x11
%patch26 -p1 -b .bdwgt3
pushd ../intel-gpu-tools-%{gputoolsdate}
%patch100 -p1 -b .cairo
popd

%build
 
#export CFLAGS="$RPM_OPT_FLAGS -fno-omit-frame-pointer"
%{?gitdate:autoreconf -v --install}

%configure \
    %{?rhel7:--enable-kms-only} \
    --disable-static \
    --enable-dri \
    --enable-xvmc \
    --enable-sna \
    --with-default-accel=uxa
make

pushd ../intel-gpu-tools-%{gputoolsdate}
autoreconf -v --install
%configure --disable-nouveau --disable-dumper
make
popd

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

pushd ../intel-gpu-tools-%{gputoolsdate}
make install DESTDIR=$RPM_BUILD_ROOT
popd

find $RPM_BUILD_ROOT -regex ".*\.la$" | xargs rm -f --
find $RPM_BUILD_ROOT -name '*asm*' | xargs rm -f --

# paranoia for building outside of mock (sigh)
rm -f $RPM_BUILD_ROOT%{_bindir}/intel-virtual-output

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc COPYING
%{driverdir}/intel_drv.so
%{_libdir}/libI810XvMC.so.1*
%{_libdir}/libIntelXvMC.so.1*
%{_libexecdir}/xf86-video-intel-backlight-helper
%{_datadir}/polkit-1/actions/org.x.xf86-video-intel.backlight-helper.policy
%{_mandir}/man4/i*

%files devel
%defattr(-,root,root,-)
%{_libdir}/libI810XvMC.so
%{_libdir}/libIntelXvMC.so

%files -n intel-gpu-tools
%defattr(-,root,root,-)
%doc COPYING
%{_bindir}/intel_*
%{_mandir}/man1/intel_*.1*

%changelog
* Tue May 05 2015 Adam Jackson <ajax@redhat.com> 2.99.911-8
- Fix URB allocation sizing on Broadwell GT3

* Thu Feb 26 2015 Adam Jackson <ajax@redhat.com> 2.99.911-7
- Enable Broadwell acceleration.

* Wed Aug 27 2014 Adam Jackson <ajax@redhat.com> 2.99.911-6
- Disable accel by default on Broadwell; enable it with Option "NoAccel" "0"
  in xorg.conf.

* Tue Aug 05 2014 Adam Jackson <ajax@redhat.com> 2.99.911-5
- Fix build outside of mock

* Tue Jun 03 2014 Adam Jackson <ajax@redhat.com> 2.99.911-4
- Fix intel_drv.so to not link libX11

* Mon Jun 02 2014 Dave Airlie <airlied@redhat.com> 2.99.911-3
- add UXA MST support.

* Wed May 07 2014 Adam Jackson <ajax@redhat.com> 2.99.911-2
- Default to UXA pre-Broadwell, as in 2.21.15

* Wed May 07 2014 Adam Jackson <ajax@redhat.com> 2.99.911-1
- intel 2.99.911
- changelog trim of pre-RHEL6 content

* Wed Apr 23 2014 Adam Jackson <ajax@redhat.com> 2.21.15-1
- intel 2.21.15

* Tue Sep 10 2013 Adam Jackson <ajax@redhat.com> 2.21.12-2
- Don't package gen4asm stuff

* Tue Jul 23 2013 Adam Jackson <ajax@redhat.com> 2.21.12-1
- intel 2.21.12

* Tue Jun 25 2013 Adam Jackson <ajax@redhat.com> 2.21.10-1
- intel 2.21.10
- new i-g-t snapshot

* Fri Sep 21 2012 Adam Jackson <ajax@redhat.com> 2.20.8-1
- intel 2.20.8

* Wed Aug 22 2012 airlied@redhat.com - 2.20.2-2
- rebuild for server ABI requires

* Wed Aug 01 2012 Adam Jackson <ajax@redhat.com> 2.20.2-1
- intel 2.20.2 (#835236)

* Wed May 16 2012 Adam Jackson <ajax@redhat.com> 2.16.0-4
- intel-2.16.0-bromolow.patch: Add support for Ivybridge GT2 Server (#821521)

* Mon May 07 2012 Adam Jackson <ajax@redhat.com> 2.16.0-2
- redhat-intel-crtc-dpms.patch: Fix some multihead transitions when X is
  started with the lid closed. (#692776)

* Mon Aug 15 2011 Adam Jackson <ajax@redhat.com> 2.16.0-1
- intel 2.16.0 (#684313)

* Mon Jul 25 2011 Adam Jackson <ajax@redhat.com> 2.15.0-2
- intel-2.15-stable.patch: Backports from master.

* Tue Jun 28 2011 Adam Jackson <ajax@redhat.com> 2.15.0-1
- intel 2.15.0 (#713767)
- intel-gpu-tools snapshot

* Thu Jan 13 2011 Adam Jackson <ajax@redhat.com> 2.14.0-1
- intel 2.14.0 (#667564)
- intel-gpu-tools snapshot

* Fri Aug 13 2010 Adam Jackson <ajax@redhat.com> 2.11.0-7
- intel-no-sandybridge.patch: Don't try to bind to snb devices (#624132)

* Fri Jun 25 2010 Dave Airlie <airlied@redhat.com> 2.11.0-6
- intel-2.11.0-fix-rotate-flushing-965.patch: fix rotated lags (#604024)

* Fri Jun 04 2010 Dave Airlie <airlied@redhat.com> 2.11.0-5
- fix X -nr (requires kernel 2.6.32-33 to work).

* Mon May 03 2010 Adam Jackson <ajax@redhat.com> 2.11.0-4
- intel-2.11-no-pageflipping.patch: Disable pageflipping (#588421)

* Fri Apr 30 2010 Bastien Nocera <bnocera@redhat.com> 2.11.0-3
- Add MacBook backlight support

* Mon Apr 26 2010 Adam Jackson <ajax@redhat.com> 2.11.0-2
- intel-2.11.0-vga-clock-max.patch: Clamp VGA pixel clock to 250MHz,
  anything higher's going to look awful anyway. (#559426)

* Fri Apr 16 2010 Adam Jackson <ajax@redhat.com> 2.11.0-1
- intel 2.11.0
- new gpu tools snapshot
