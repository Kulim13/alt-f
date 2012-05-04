#!/bin/sh

. common.sh
write_header "Alt-F Login"

SECR=/etc/web-secret

mktt tt_login "Enter your web administration password, the session is valid for one hour.<br>The box date must be correct for the password to be accepted."
mktt tt_again "Type your password again. It will be your \"root\" password."

cat<<-EOF
    <center>
	<form action="/cgi-bin/login_proc.cgi" method="post">
    <table>
	<tr><td>Password:</td>
		<td><input type="password" autocomplete="off" name="passwd" $(ttip tt_login)></td>
EOF

if ! test -e $SECR; then
	cat<<-EOF
		</tr>
		<tr><td>Again:</td>
			<td><input type="password" autocomplete="off" name="passwd_again" $(ttip tt_again)></td>
	EOF
fi

cat<<-EOF
		<td><input type="submit" value="Submit"></td>
	</tr>
	</table>
	<input type="hidden" name=from_url value="$(basename $REQUEST_URI)">
	</form></center>
	</body></html>
EOF