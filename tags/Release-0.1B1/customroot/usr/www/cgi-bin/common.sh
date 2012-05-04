
# sed removes any ' that would upset quoted assignment
# awk ensures that 
#	- all variables passed have legal names
#	- special characters are not interpreted by sh
read_args() {
	read -r args
	eval $(echo -n $args | tr '\r' '\n' | sed -e 's/'"'"'/%27/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$1~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$1,39,$2,39}')

	# some forms needs key=value evaluated as value=key,
	# so reverse and evaluate them
	eval $(echo -n $args |  sed -e 's/'"'"'/%27/g' | \
		awk 'BEGIN{RS="&";FS="="}
			$2~/^[a-zA-Z][a-zA-Z0-9_]*$/ {
			printf "%s=%c%s%c\n",$2,39,$1,39}' )                
}

# return n+1 argument. If called as "lsh 2 one two three" returns "two"
lsh () {
	shift $1
	echo $1
}

checkip() {
	echo "$1" | grep -q -e '^[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}$'
}

checkmac() {
	echo "$1" | grep -q -e '^\([a-fA-F0-9]\{2\}:\)\{5\}[a-fA-F0-9]\{2\}$'
}

checkname() {
	echo "$1" | grep -v -q -e '^[^a-zA-Z]' -e '[^a-zA-Z0-9-].*'
}

eatspaces() {
	echo $* | tr -d ' '
}

html_header() {
	echo -e "Content-Type: text/html; charset=UTF-8\n\n<html><body>"
}

debug() {
	echo -e "Content-Type: text/html; charset=UTF-8\n\n<html><body><pre>$(set)</pre>"
}

enddebug() {
	echo "</body></html>"
}

msg() {
	echo "Content-Type: text/html; charset=UTF-8;

	<html><body>
	<script type=text/javascript>
	alert(\"$1\")
	window.history.back()
//	window.location.reload(window.history.back())
	</script>
	</body></html>"
	exit 1
}

back_button() {
	echo "<input type=button value=\"Back\" onclick=\"history.back()\">"
}

select_part() {
	echo "<select name=part>"
	echo "<option value=none>Select a partition</option>"

	df -h | while read ln; do

	part=""
	eval $(echo $ln | awk '/^\/dev\//{printf "part=%s; pcap=%s; avai=%s", \
		$1, $2, $4}')
	if test -z $part; then continue; fi
	partl=$(plabel $part)
	if test -z "$partl"; then partl=$(basename $part); fi

	res=$(mdadm --query --detail --test --export $part 2>/dev/null )
	if test $? = 4; then
		dsk=$(basename $part)
		mod=$(cat /sys/block/${dsk%%[1-9]}/device/model) >/dev/null 2>&1
		if test -z "$mod"; then continue; fi
		dcap=$(awk -v sz=$(cat /sys/block/${dsk%%[1-9]}/size) 'BEGIN{printf "%.1f", sz*512/1e9}' /dev/null)
	else
		eval $res
		mod=$MD_LEVEL
		dcap=$pcap
	fi

	echo "<option value=$part> $partl ($mod, ${dcap}GB)</option>"
	done
	echo "</select>"
}

gotopage() {
	cat<<-EOF
		HTTP/1.1 303
		Content-Type: text/html; charset=UTF-8
		Location: $1
	
	EOF
        exit 0
}

check_cookie() {
	eval $HTTP_COOKIE >& /dev/null
	if test -e "/tmp/cookie"; then
		if test "$(cat /tmp/cookie)" = "${ALTFID}"; then
			return
		fi
	fi
	gotopage /cgi-bin/login.cgi?$REQUEST_URI
}

# args: title [refresh time]
write_header() {
	cat<<-EOF
		Content-Type: text/html; charset=UTF-8

		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<html><head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	EOF

	if test $# == 2; then
		echo "<meta http-equiv=\"refresh\" content=\"$2\">"
	fi
	cat <<-EOF
		<title>$1</title>
		</head><body>
		<center><h2>$1</h2></center>
	EOF
}
