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
Version: 1.17.2
Release: 1.0.ysu1.1%{?dist}
License: GPLv2

# Extracted from latest XS intel-ice package update
Source0: intel-ice-1.17.2.tar.gz

Patch0: fix-enabling-sr-iov-with-xen.patch
Patch1: fix-kcompat-order.patch

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
%{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
%{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

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
* Thu Oct  9 2025 Yann Sionneau <yann.sionneau@vates.tech> - 1.17.2-1
- Update driver to v1.17.2
- Synced from XS driver SRPM intel-ice-1.17.2-1.xs8.src.rpm

* Mon Aug 21 2023 Gael Duperrey <gduperrey@vates.fr> - 1.8.8-1
- initial package, version 1.8.8
- Synced from XS driver SRPM intel-ice-1.8.8-1.el7.centos.src.rpm
- change firmware to live in /lib/firmware/override
