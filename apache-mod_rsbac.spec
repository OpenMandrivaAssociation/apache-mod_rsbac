#Module-Specific definitions
%define apache_version 2.2.13
%define mod_name mod_rsbac
%define modversion 31
%define mod_conf 11_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	brings some RSBAC specific features to Apache
Name:		apache-%{mod_name}
Version:	0
Release:	%mkrel 0.svn.%{modversion}.4
Group:		System/Servers
License:	GPLv2+
URL:		http://svn.rsbac.org/?do=browse&project=rsbac-apache&path=/
Source0:	%{mod_name}-%{modversion}.tar.bz2
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= %{apache_version}
Requires(pre):  apache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache-mpm-rsbac >= %{apache_version}
Requires:	rsbac-admin, kernel-rsbac
BuildRequires:  apache-devel >= %{apache_version}
BuildRequires:	rsbac-admin-devel >= 1.4.2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_rsbac brings some RSBAC specific features to Apache, namely:
- rsbac_jail, can jail the whole Apache environment. Work like mod_chroot.
- RC, working until now only with the Prefork MPM.

The RC module allow a SuExec-like functionality without the cost of forking
new processes, and thus much faster.
The master Apache process is assigned a role (apache-master) which is allowed
to assign to role apache-worker to the worker processes it creates (also
called childrens).
Every worker is then allowed to switch their role to a set of roles, which
represent either the different directories or virtual hosts to serve.

You can use either the Jail functions, either RC functions or both at the
same time.

Of course, you need a RSBAC enabled kernel to use mod_jail.
See http://www.rsbac.org/ or install a RSBAC enabled kernel.

%prep

%setup -q -n %{mod_name}-%{modversion}

%build

%{_sbindir}/apxs -c -lrsbac -DKERNEL_NEXT mod_rsbac.c
#%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_docdir}/apache-mod_rsbac

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
cat << EOF > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}
LoadModule rsbac_module extramodules/%{mod_so}
<IfModule prefork.c>
	WorkerRole 80
</IfModule>
#JailDir /var/www
EOF

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
	if [ -f %{_var}/lock/subsys/httpd ]; then
		%{_initrddir}/httpd restart 1>&2
	fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CAVEATS README TODO 
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}

