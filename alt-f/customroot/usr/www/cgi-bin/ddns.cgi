#!/bin/sh

PATH=/bin:/usr/bin:/sbin:/usr/sbin

. common.sh

check_cookie
write_header "Dynamic DNS Setup"

CONFF=/etc/inadyn.conf

cat<<EOF
	<script type="text/javascript">
	function val() {
		idx = document.formd.provider.selectedIndex
		prov = document.formd.provider.options[idx].value
		if (prov == "freedns.afraid.org") {
			document.formd.user.disabled = true;
			document.formd.passwd.disabled = true;
			document.getElementById("po").innerHTML = 
"hostname,<a href=http://inatech.eu/inadyn/readme.html#special_freedns target=_blank>hash:</a>"
		} else {
			document.formd.user.disabled = false;
			document.formd.passwd.disabled = false;
			document.getElementById("po").innerHTML = "hostname:"
		}
	}
	</script>
EOF

if test -f $CONFF; then
	while read line; do
		eval $(echo $line | awk '!/#/{if (NF == 2) print $1 "=" $2}')
	done < $CONFF

	case $dyndns_system in
		dyndns@dyndns.org) dyndns=selected ;;
		default@zoneedit.com) zoneedit=selected ;;
		default@no-ip.com)  noip=selected ;;
		default@freedns.afraid.org)
			updis=disabled
			freedns=selected
			;;
	esac
fi

cat<<-EOF
	<form name="formd" action="/cgi-bin/ddns_proc.cgi" method="post">

	<table><tr>
		<td> provider:</td>
		<td><select name="provider" onchange="val()">
			<option> Select one
			<option $dyndns> dyndns.org
			<option $freedns> freedns.afraid.org
			<option $zoneedit> zoneedit.com
			<option $noip> no-ip.com
		</select></td></tr>
	<tr><td><div id=po>hostname:</div</td>
		<td><input type="text" value="$alias" name="host" ></td></tr>
	<tr><td>username:</td>
		<td><input type="text" $updis value="$username" name="user"></td></tr>
	<tr><td>password:</td>
		<td><input type="password" $updis value="$password" name="passwd"></td></tr>
	<tr><td></td><td><br><input type="submit" value="Submit">$(back_button)</tr>	
	</table></form></body></html>
EOF
