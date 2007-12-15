#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	vserver		# kernel build without vserver & grsecurity

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		_cvsdate	20071017
%define		_rel		0.%{_cvsdate}.6
Summary:	aufs - Another Unionfs
Summary(pl.UTF-8):	aufs (Another Unionfs) - inny unionfs
Name:		aufs
Version:	0
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	%{name}-%{_cvsdate}.tar.bz2
# Source0-md5:	dee001829acbf3a4fa857a752527b385
Patch0:		%{name}-vserver.patch
URL:		http://aufs.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
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

%description -l pl.UTF-8
Początkowo aufs był całkowicie przeprojektowanym i od nowa
zaimplementowanym unionfs-em. Po wielu oryginalnych pomysłach,
podejściach, poprawkach i implementacjach stał sie całkowicie innym
niż unionfs zachowując podstawowe możliwości. unionfs jest rozwijany
przez profesora Ereza Zadoka w Stony Brook University i jego zespół.
Nie znający unionfs-a powinni spróbować go i poznać przed używaniem
aufs-a. Część terminologii wywodzi się z unionfs-a.

%package -n kernel%{_alt_kernel}-fs-aufs
Summary:	Linux driver for aufs
Summary(pl.UTF-8):	Sterownik dla Linuksa do aufs
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-fs-aufs
This is driver for aufs for Linux.

This package contains Linux module.

%description -n kernel%{_alt_kernel}-fs-aufs -l pl.UTF-8
Sterownik dla Linuksa do aufs.

Ten pakiet zawiera moduł jądra Linuksa.

%prep
%setup -qn %{name}
%if %{with vserver}
%patch0 -p1
%endif

sed '
	s/$(CONFIG_AUFS)/m/; 
	%{!?debug:s/$(CONFIG_AUFS_DEBUG.*)/n/}; 
	s/$(CONFIG_AUFS_HINOTIFY)/n/;
	s/$(CONFIG_AUFS_EXPORT)/y/;
	s/$(CONFIG_AUFS_SYSAUFS)/n/
' -i fs/aufs/Makefile
cp -a include/linux fs/aufs

%build
%if %{with kernel}
%build_kernel_modules -C fs/aufs -m aufs \
	EXTRA_CFLAGS=" \
		-DCONFIG_AUFS_BRANCH_MAX_127 \
		-DCONFIG_AUFS_BRANCH_MAX_CHAR \
		-DCONFIG_AUFS_FAKE_DM \
		-DCONFIG_AUFS_MODULE \
		-UCONFIG_AUFS_KSIZE_PATCH \
		%{?debug:-DCONFIG_AUFS_DEBUG} \
		%{?with_vserver:-DVSERVER} \
	"
%endif

%if %{with userspace}
%{__make} -C util \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -DCONFIG_AUFS_BRANCH_MAX_127"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_mandir}/man5,%{_sbindir}}
install util/{mount.aufs,umount.aufs,auplink,aulchown} $RPM_BUILD_ROOT%{_sbindir}
install util/aufs.5 $RPM_BUILD_ROOT%{_mandir}/man5/
%endif

%if %{with kernel}
%install_kernel_modules -m fs/aufs/aufs -d kernel/fs/aufs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-fs-aufs
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-fs-aufs
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-fs-aufs
%defattr(644,root,root,755)
%dir /lib/modules/%{_kernel_ver}/kernel/fs/aufs
/lib/modules/%{_kernel_ver}/kernel/fs/aufs/*.ko*
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README History
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man5/*
%endif
