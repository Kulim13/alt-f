#!/bin/sh

. common.sh
check_cookie

write_header "uShare Setup"

CONFF=/etc/ushare.conf

if test -e $CONFF; then
	USHARE_DIR="$(awk -F= '/^USHARE_DIR/{print $2}' $CONFF)" 
	eval $(grep ^USHARE_PORT $CONFF)
	webhost="$(hostname -i | tr -d ' '):$USHARE_PORT/web/ushare.html"
	eval $(grep ^ENABLE_WEB $CONFF)
	if test "$ENABLE_WEB" = "yes"; then
		chkweb="checked"
	fi
fi

webbut="enabled"
rcushare status >& /dev/null
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

	<form name=transmission action=ushare_proc.cgi method="post" >
	<table><tr>
EOF

OIFS="$IFS"; IFS=','; k=1
for i in $USHARE_DIR; do
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