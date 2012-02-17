#!/bin/sh

. common.sh

check_cookie
write_header "Disk Utilities" "" "document.disku.reset()"

CONFT=/etc/misc.conf

mktt power_tt "Higher power savings, lower performance, can spindow<br>
Medium power savings and performance, can spindow<br>
Low power saving, higher performance, can't spindown.<br>
If disabled, the disk does not support Adv. Power Mode."

mktt spindown_tt "After this minutes of inactivity the disk will spin down,<br>
depending on the Power Saving Settings"

has_disks

if test -f $CONFT; then
	. $CONFT
fi
for i in HDSLEEP_LEFT HDSLEEP_RIGHT HDSLEEP_USB HDPOWER_LEFT HDPOWER_RIGHT; do
	if test -z "$(eval echo \$$i)"; then
		eval $(echo $i=0)
	fi
done


cat<<EOF
	<script type="text/javascript">
	function submit() {
			document.getElementById("diskf").submit;
	}
	</script>

	<form id=disku name=disku action="/cgi-bin/diskutil_proc.cgi" method="post">
	<fieldset><Legend><strong> Disks </strong></legend>
	<table>
	<tr align=center><th>Bay</th>
	<th>Dev.</th>
	<th>Capacity</th>
	<th>Disk Model</th>
	<th></th>
	<th>Health</th>
	<th>Power Mode</th>
	<th>Power Sav.</th>
	<th columnspan=2>Spindow</th> 
EOF

for disk in $disks; do
	dsk=$(basename $disk)
	disk_details $dsk

	power_dis="disabled"
	if hdparm -I $disk | grep -q "Adv. Power Management"; then
		power_dis=""
	fi

	stat=$(disk_power $dsk)
	paction="StandbyNow"
	paction_dis=""
	if test "$stat" = "standby"; then
		paction="WakeupNow"
	elif test "$stat" = "unknown"; then
		paction="Unknown"
		paction_dis="disabled"
	fi

	ejectop="Eject"
	if eject -s $dsk > /dev/null; then
		ejectop="Load"
	fi

	eval $(echo $dbay | awk '{
		printf "hdtimeout=HDSLEEP_%s; hdtimeout_val=$HDSLEEP_%s; power=HDPOWER_%s; power_val=$HDPOWER_%s", toupper($1), toupper($1), toupper($1), toupper($1)}')

	medpower_sel=""; highpower_sel=""; lowpower_sel=""
	case $power_val in
		1) highpower_sel="selected" ;;
		127) medpower_sel="selected" ;;
		254) lowpower_sel="selected" ;;
	esac
	
	cat<<-EOF	 
		<tr><td>$dbay</td><td>$dsk</td><td>$dcap</td><td>$dmod</td>
		<td> <input type="submit" name="$dsk" value="$ejectop"></td>
		<td><select name="$dsk" onChange=submit()>
			<option value="">Select Action</option>
			<option value="hstatus">Show Status</option>
			<option value="shorttest">Start short test</option>
			<option value="longtest">Start long test</option>
			</select></td>
		<td> <input type="submit" $paction_dis name="$dsk" value="$paction"> </td>
		<td><select $power_dis name=$power $(ttip power_tt)>
			<option $highpower_sel value=1>High</option>
			<option $medpower_sel value=127>Medium</option>
			<option $lowpower_sel value=254>Low</option>
			</select></td>
		<td><input type="text" size=2 name="$hdtimeout" value="$hdtimeout_val" $(ttip spindown_tt)> min.</td></tr>
	EOF
done

cat<<-EOF
	<tr><td colspan=7></td>
	<td colspan=2 align=center><input type="submit" name="standby" value="        Submit        "></td></tr>        
	</table></fieldset><br>
	</form></body></html>
EOF