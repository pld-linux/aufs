#
# TODO:
# - define CONFIG_ option directly
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		subver		20090315
%define		prel		0.%{subver}.%{rel}

%define		pname		aufs
%define		rel		6
Summary:	aufs - Another Unionfs
Summary(pl.UTF-8):	aufs (Another Unionfs) - inny unionfs
Name:		%{pname}%{_alt_kernel}
Version:	0
Release:	%{prel}
License:	GPL v2
Group:		Base/Kernel
Source0:	%{pname}-%{subver}.tar.bz2
# Source0-md5:	f2cb8c2dcf40ed076b1fcdcb1e91412e
Patch0:		%{pname}-vserver.patch
#Patch1:		%{pname}-disable-security_inode_permission.patch
Patch2:		%{pname}-fixes.patch
#Patch3:		%{pname}-spin_lock.patch
Patch4:		%{pname}-apparmor.patch
Patch5:		%{pname}-br-xfs-fix.patch
Patch6:		%{pname}-vfsub.c.patch
URL:		http://aufs.sourceforge.net/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.25.2}
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
Release:	%{prel}@%{_kernel_ver_str}
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
%setup -qn %{pname}
%patch0 -p1
#%patch1 -p1
%patch2 -p1
#%patch3 -p1
%if "%{_kernel_ver}" < "2.6.30"
if [ -d %{_kernelsrcdir}/security/apparmor ]; then
%patch4 -p1
fi
%endif
%patch5 -p1
if [ -d %{_kernelsrcdir}/fs/unionfs ]; then
%patch6 -p0
%if "%{_kernel_ver}" >= "2.6.30"
else
%patch6 -p0
%endif
fi

cp -a include/linux fs/aufs25

%build
%if %{with kernel}
if [ -f %{_kernelsrcdir}/include/linux/vs_base.h &&
     ! -d %{_kernelsrcdir}/security/apparmor ]; then
	isvserver="-DVSERVER"
fi
%ifarch %{x8664} ia64 ppc64 sparc64
	ino_t64="-DCONFIG_AUFS_INO_T_64"
%endif

export CONFIG_AUFS=m
export CONFIG_AUFS_BR_XFS=y
%build_kernel_modules -C fs/aufs25 -m aufs \
	EXTRA_CFLAGS+=" \
		-DCONFIG_AUFS_BRANCH_MAX_127 \
		-DCONFIG_AUFS_BRANCH_MAX_CHAR \
		-DCONFIG_AUFS_FAKE_DM \
		-DCONFIG_AUFS_MODULE \
		-UCONFIG_AUFS_KSIZE_PATCH \
		-UCONFIG_AUFS_DLGT \
%if "%{_alt_kernel}" != "vanilla"
		-DCONFIG_AUFS_UNIONFS23_PATCH \
		-DCONFIG_AUFS_UNIONFS22_PATCH \
		-DCONFIG_AUFS_SPLICE_PATCH \
%endif
		%{?debug:-DCONFIG_AUFS_DEBUG} \
		$isvserver \
		$ino_t64"
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
%install_kernel_modules -m fs/aufs25/aufs -d kernel/fs/aufs
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
%doc README.aufs1 README.aufs2 History
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man5/*
%endif
