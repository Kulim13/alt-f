#!/bin/sh

. common.sh
check_cookie

write_header "fuppes Setup"

CONFF=/etc/fuppes/fuppes.cfg

if test -e $CONFF; then # damned spaces in file names!
	sed -i '/<!--<dir>/d' $CONFF	
	FUPPES_DIR="$(sed -n '/<shared_objects>/,/<\/shared_objects>/s/.*<dir>\(.*\)<\/dir>/\1:/p }' $CONFF)"

	FUPPES_PORT=$(sed -n 's/.*<http_port>\(.*\)<\/http_port>/\1/p' $CONFF)
	webhost="$(hostname -i | tr -d ' '):$FUPPES_PORT/presentation/config.html"

	aip=$(sed -n '/<allowed_ips>/,/<\/allowed_ips>/p' $CONFF | awk ' \
		/<ip>/ && ! /<!--/ { \
		printf "%s", substr($1,5,length($1)-9)}')
	if test -z "$aip"; then
		chkweb="checked"
	fi
fi

webbut="enabled"
rcfuppes status >& /dev/null
if test $? != 0 -o "$chkweb" != "checked"; then
		webbut="disabled"
fi

cat<<-EOF
	<script type="text/javascript">
		function browse_dir_popup(input_id) {
			start_dir = document.getElementById(input_id).value;
			if (start_dir == "")
				start_dir="/mnt";
			window.open("browse_dir.cgi?id=" + input_id + "?browse=" + start_dir, "Browse", "scrollbars=yes, width=500, height=500");
			return false;
		}
		function edisable(chk, but, st) {
			if (st == "disabled")
				return;
			if (document.getElementById(chk).checked == true)
				document.getElementById(but).disabled = false;
			else
				document.getElementById(but).disabled = true;
		}
	</script>

	<form name=fuppes action=fuppes_proc.cgi method="post" >
	<table><tr>
EOF

OIFS="$IFS"; IFS=':'; k=1
for i in $FUPPES_DIR; do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id=conf_dir_$k name=sdir_$k value="$i"></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$k')" value=Browse></td>
		</tr>
	EOF
    k=$((k+1))
done
IFS="$OIFS"

for j in $(seq $k $((k+2))); do
	cat<<-EOF
		<tr><td>Share directory</td>
		<td><input type=text size=32 id=conf_dir_$j name=sdir_$j value=""></td>
		<td><input type=button onclick="browse_dir_popup('conf_dir_$j')" value=Browse></td>
		</tr>
	EOF
done

cat<<-EOF
	<tr><td>Enable Web</td><td><input type=checkbox id=chkweb $chkweb name="ENABLE_WEB" value="yes" onclick="edisable('chkweb','webbut', '$webbut')"></td></tr>
	<tr><td></td><td>
	<input type=hidden name=cnt value=$j>
	<input type=submit value=Submit> $(back_button)
		<input type="button" id=webbut $webbut value="WebPage" onClick="document.location.href='http://$webhost';">
	</td></tr></table></form></body></html>
EOF