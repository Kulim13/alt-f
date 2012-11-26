#!/bin/sh

m2g() {
    if test "$1" -ge 1000; then
        #echo "$(expr $1 / 1000)GB"
		echo $1 | awk '{printf "%.1fGB", $1/1000}'
    else
        echo "${1}MB"
    fi
}

. common.sh
check_cookie
read_args

wdir=$(httpd -d "$newdir")
wdir=$(echo "$wdir" | sed -n 's/^ *//;s/ *$//p')
bdir=$(dirname "$wdir")
#nbdir=$(echo "$bdir" | sed 's|\([\&\|]\)|\\\1|g')
nbdir=$(urlencode "$bdir")

#echo -e "$0: HTTP_REFERER=$HTTP_REFERER\nnbdir=$nbdir" >> /tmp/foo

#debug
#set -x

if ! echo "$wdir" | grep -q '^/mnt'; then
	msg "Only operations on /mnt sub-folders are allowed"
fi

if test -n "$srcdir"; then
	srcdir=$(httpd -d "$srcdir")
fi

if test -n "$CreateDir"; then
	if test -d "$wdir"; then
		msg "Can't create, folder \"$wdir\" already exists."
	elif test -d "$bdir"; then
		res=$(mkdir "$wdir" 2>&1 )
		if test $? != 0; then
			msg "$res"
		fi
		HTTP_REFERER=$(echo "$HTTP_REFERER" | sed "s|?browse=.*|?browse=$newdir|")
	else
		msg "Can't create, parent folder \"$bdir\" does not exists."
	fi
	
elif test -n "$DeleteDir"; then
	if ! test -d "$wdir"; then
		msg "Can't delete, folder \"$wdir\" does not exists."
	fi

	src_sz=$(du -sm "$wdir" | cut -f1)
	terr=$(mktemp -t)

	html_header "Deleting $(m2g $src_sz) \"$wdir\" folder"
	cat<<-EOF
		<div id="ellapsed" style="position: relative; z-index: -1;
		width: 30%; left: 30%; background-color: #bdbdbd;
		text-align: right; font-size: 1.5em;"></div>
	EOF

	busy_cursor_start
	nice rm -rf "$wdir" 2> $terr &

	bpid=$!
	touch /tmp/folders_op.$bpid
	sleep_time=$(expr \( $src_sz / 10000 + 1 \) \* 100000)
	if test "$sleep_time" -gt 2000000; then sleep_time=2000000; fi
	while kill -0 $bpid >& /dev/null; do
		usleep $sleep_time
		rm_sz=$(du -sm "$wdir" 2>/dev/null | cut -f1)
		if test -z "$rm_sz"; then continue; fi
		el=$(expr $rm_sz \* 100 / $src_sz)
		cat<<-EOF
		<script type="text/javascript">
			document.getElementById("ellapsed").innerHTML = '$(drawbargraph $el $(m2g $rm_sz) | tr "\n" " " )';
		</script>
		EOF
	done
	wait $bpid
	st=$?

	busy_cursor_end

	rm -f /tmp/folders_op.$bpid
	res=$(cat $terr)
	rm -f $terr
#echo "</body></html>"
#exit 1
	if test $? != 0; then
		msg "$res"
	fi

	HTTP_REFERER=$(echo "$HTTP_REFERER" | sed 's|?browse=.*$|?browse='"$nbdir"'|')
	js_gotopage "$HTTP_REFERER"

elif test -n "$Copy" -o -n "$Move" -o -n "$CopyContent"; then
	sbn=$(basename "$srcdir")
	if ! test -d "$srcdir"; then
		msg "Folder \"$srcdir\" does not exists."
	fi

	if test -d "${wdir}/${sbn}" -a -z "$CopyContent"; then
		msg "Folder \"$wdir\" already contains a folder named \"$sbn\""
	fi

	src_mp=$(find_mp "$srcdir")
	src_sz=$(du -sm "$srcdir" | cut -f1)

	dst_mp=$(find_mp "$wdir")
	dst_free=$(df -m $dst_mp | awk '/\/mnt\//{print $4}')

	if test "$op" = "CopyContent"; then
		op="Copy Contents"
	fi

	if test -n "$Copy" -o -n "$CopyContent"; then
		if test $src_sz -gt $dst_free; then
			msg "Can't $op, $(m2g $src_sz) needed $(m2g $dst_free) available."
		fi
	elif test $src_mp != dst_mp; then
		if test $src_sz -gt $dst_free; then
			msg "Can't $op, $(m2g $src_sz) needed $(m2g $dst_free) available."
		fi
	fi

	terr=$(mktemp -t)

	html_header "$op $(m2g $src_sz) from \"$srcdir\" to \"$wdir\""
	cat<<-EOF
		<div id="ellapsed" style="position: relative; z-index: -1;
		width: 30%; left: 30%; background-color: #bdbdbd;
		text-align: right; font-size: 1.5em;"></div>
	EOF
	busy_cursor_start

	(
	if test -n "$Copy" -o -n "$CopyContent"; then
		if test -n "$CopyContent"; then
			cd "$srcdir"
			srcdir="."
		else
			cd "$(dirname "$srcdir")"
			srcdir=$(basename "$srcdir")
		fi

	# cp -a, piped tar and rsync uses too much memory (that keeps growing) for big trees and start swapping
	# cpio has constante memory usage but is limited to 4GB files...
	# cp -a makes 9MBps, cpio 6MBps on raid1 to raid1
	# looks like busybox-1.20.2 'cp' don't suffer from this problem.
if false; then
		tf=$(mktemp -t)
		xtra="cat"

		# find "$srcdir" -size +4294967c > $tf # test
		find "$srcdir" -size +4294967295c > $tf
		if test -s $tf; then
			xtra="grep -v -f $tf"
		fi

		find "$srcdir" -depth | $xtra | cpio -pdm "$wdir" 2> $terr
		st=$?
		if test "$st" = 0; then
			while read -r fn; do
				td=$(dirname "$fn")
				#echo "$fn"
				cp -dp "$fn" "$wdir/$td" 2> $terr
				st=$?
				if test "$st" != 0; then break; fi
			done < $tf
		fi
		rm -f $tf
else
		cp -a "$srcdir" "$wdir"
fi
	else
		mv -f "$srcdir" "$wdir" 2> $terr
	fi
	) &

	bpid=$!
	touch /tmp/folders_op.$bpid
	sleep_time=$(expr $src_sz / 100 + 1)
	if test $sleep_time -gt 10; then sleep_time=10; fi
	while kill -0 $bpid >& /dev/null; do
		sleep $sleep_time
		td="$wdir/$(basename "$srcdir")"
		if ! test -d "$td"; then continue; fi
		mv_sz=$(nice du -sm "$td" | cut -f1)
		el=$(expr $mv_sz \* 100 / $src_sz)
		cat<<-EOF
		<script type="text/javascript">
			document.getElementById("ellapsed").innerHTML = '$(drawbargraph $el $(m2g $mv_sz) | tr "\n" " " )';
		</script>
		EOF
	done
	wait $bpid
	st=$?

	busy_cursor_end

	rm -f /tmp/folders_op.$bpid
	res=$(cat $terr)
	rm -f $terr
#echo "</body></html>"
#exit 1
	if test $st != 0; then
		msg "$res"
	fi

	HTTP_REFERER=$(echo "$HTTP_REFERER" | sed -n 's|browse=.*$|browse='"$nbdir"'|p')
	js_gotopage "$HTTP_REFERER"

elif test -n "$Permissions"; then
	nuser="$(httpd -d $nuser)"
	ngroup="$(httpd -d $ngroup)"
		
	if test -z "$recurse"; then
		optr="-maxdepth 0"
	fi

	if test -z "$toFiles"; then
		optf="-type d"
	fi

	if test -n "$setgid"; then
		setgid="s"
	fi

	find "$wdir" $optr $optf -exec chown "${nuser}:${ngroup}" {} \;
	find "$wdir" $optr $optf -exec chmod u=$p2$p3$p4,g=$p5$p6$p7$setgid,o=$p8$p9$p10 {} \;

	HTTP_REFERER=$(httpd -d "$goto")
fi

#enddebug
#echo -e "$0: HTTP_REFERER2=$HTTP_REFERER" >> /tmp/foo
gotopage "$HTTP_REFERER"

