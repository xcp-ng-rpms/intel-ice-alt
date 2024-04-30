%define vendor_name Intel
%define vendor_label intel
%define driver_name ice

# XCP-ng: install to the override directory
%define module_dir override

## kernel_version will be set during build because then kernel-devel
## package installs an RPM macro which sets it. This check keeps
## rpmlint happy.
%if %undefined kernel_version
%define kernel_version dummy
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}-alt
Version: 1.11.17.1
Release: 1%{?dist}
License: GPLv2

# Extracted from latest XS driver disk
Source0: intel-ice-1.11.17.1.tar.gz
Patch0: fix-enabling-sr-iov-with-xen.patch
Patch1: 0001-CP-47698-Change-module-name-intel_auxiliary-to-intel.patch

# XCP-ng patches
Patch1000: 0001-Look-for-firmware-in-lib-firmware-override.patch

BuildRequires: gcc
BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n %{vendor_label}-%{driver_name}-%{version}

%build
%{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build NEED_AUX_BUS=2 modules

%install
%{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true NEED_AUX_BUS=2 modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

DDP_PKG_DEST_PATH=%{buildroot}/lib/firmware/override/%{vendor_label}/%{driver_name}/ddp
mkdir -p ${DDP_PKG_DEST_PATH}
install -m 644 $(pwd)/ddp/%{driver_name}-*.pkg ${DDP_PKG_DEST_PATH}
(cd ${DDP_PKG_DEST_PATH} && ln -sf %{driver_name}-*.pkg %{driver_name}.pkg)

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko
/lib/firmware/override/*

%changelog
* Tue Apr 30 2024 Gael Duperrey <gduperrey@vates.tech> - 1.11.17.1-1
- Update to version 1.11.17.1
- Synced from XS driver SRPM intel-ice-1.11.17.1-4.xs8~2_1.src.rpm

* Mon Aug 21 2023 Gael Duperrey <gduperrey@vates.fr> - 1.8.8-1
- initial package, version 1.8.8
- Synced from XS driver SRPM intel-ice-1.8.8-1.el7.centos.src.rpm
- change firmware to live in /lib/firmware/override
