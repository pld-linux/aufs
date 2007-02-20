# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_rel	0.1
Summary:	Aufs - Another Unionfs
Name:		aufs
Version:	0
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	%{name}-20070220.tar.bz2
# Source0-md5:	81bc264f83a3cdd579e0bffcbf5f0d74
URL:		http://aufs.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
In the early days, aufs was entirely re-designed and re-implemented
Unionfs. After many original ideas, approaches, improvements and
implementations, it becomes totally different from Unionfs while
keeping the basic features. Unionfs is being developed by Professor
Erez Zadok at Stony Brook University and his team. If you don't know
Unionfs, I recommend you to try and know it before using aufs. Some
terminology in aufs follows Unionfs's.

%package -n kernel%{_alt_kernel}-fs-aufs
Summary:	Linux driver for aufs
Summary(pl.UTF-8):	Sterownik dla Linuksa do aufs
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-fs-aufs
This is driver for aufs for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-aufs -l pl.UTF-8
Sterownik dla Linuksa do aufs.

Ten pakiet zawiera moduł jądra Linuksa.

%package -n kernel%{_alt_kernel}-smp-fs-aufs
Summary:	Linux SMP driver for aufs
Summary(pl.UTF-8):	Sterownik dla Linuksa SMP do aufs
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-fs-aufs
This is driver for aufs for Linux.

This package contains Linux SMP module.

%description -n kernel%{_alt_kernel}-smp-fs-aufs -l pl.UTF-8
Sterownik dla Linuksa do aufs.

Ten pakiet zawiera moduł jądra Linuksa SMP.

%prep
%setup -qn %{name}
sed 's/$(CONFIG_AUFS)/m/; %{!?debug:s/$(CONFIG_AUFS_DEBUG.*)/n/}; s/$(CONFIG_AUFS_HINOTIFY)/n/' -i fs/aufs/Makefile
cp -a include/linux fs/aufs

%build
%if %{with kernel}
%build_kernel_modules -C fs/aufs -m aufs \
	EXTRA_CFLAGS="-DCONFIG_AUFS_BRANCH_MAX_CHAR -DCONFIG_AUFS_FAKE_DM -DCONFIG_AUFS_MODULE -UCONFIG_AUFS_KSIZE_PATCH %{?debug:-DCONFIG_AUFS_DEBUG}"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m fs/aufs/aufs -d fs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-fs-aufs
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-fs-aufs
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-fs-aufs
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-fs-aufs
%depmod %{_kernel_ver}smp

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-fs-aufs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/fs/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-fs-aufs
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/fs/*.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README History
%endif
