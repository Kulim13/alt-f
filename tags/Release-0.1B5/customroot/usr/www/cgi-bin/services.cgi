#!/bin/sh

. common.sh
check_cookie

#debug

CONFD=/etc/init.d/
CONFF=/etc/inetd.conf

pg=$(basename $SCRIPT_NAME)
action=${pg:0:3}

for i in $(ls -r $CONFD); do
	if $(grep -q "^TYPE=$action" $CONFD/$i); then
		srv="$srv ${i:3}" 
	fi
done

case $action in
	net)
		title="Network Services"
		;;
	sys)
		title="System Services"
		;;
	use) # hellas, should be "user"
		title="User Services"
		;;
esac

write_header "$title"
	
s="<strong>"
es="</strong>"

if test -z "$srv"; then
	echo "<center><h4>No services available</h4></center></body></html>"
	exit 0;
fi

cat<<-EOF
	<form action="/cgi-bin/services_proc.cgi" method="post">
	<table><tr>
	<th>Service</th>
	<th align=center>Boot Enabled</th>
	<th align=center>Status</th>
	<th align=center>Action</th>
	<th></th>
	<th align=left>Description</th></tr>
EOF

for i in $srv; do
	eval $(grep '^DESC=' $CONFD/S??$i)

	chkf=""
	if test -x /etc/init.d/S??$i; then
		chkf="CHECKED"
	fi

	if rc$i status >/dev/null ; then
		st="<strong> Running</strong>"
		act="StopNow"
	else
		st="Stopped"
		act="StartNow"
	fi

	if test -f $PWD/${i}.cgi; then
		conf="<td><input type="submit" name=$i value="Configure"></td>"
	else
		conf="<td></td>"
	fi

	cat<<-EOF
		<tr><td> $i </td>
		<td align=center><input type=checkbox $chkf name=$i value=enable></td>
		<td>$st</td>
		<td><input type="submit" name=$i value="$act"></td>
		$conf
		<td>$DESC</td></tr>
	EOF
done

cat<<-EOF
	<tr><td></td>
	<td><input type="submit" name="$srv" value="Submit"></td></tr>
	</table>
	</form></body></html>
EOF

#enddebug
