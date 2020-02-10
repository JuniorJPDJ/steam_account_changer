#!/bin/bash

STEAMDIR="$HOME/.local/share/Steam"
STEAMUSERDATA="$STEAMDIR/userdata"
STEAMREGISTRY="$HOME/.steam/registry.vdf"

get_name() {
	grep PersonaName "$STEAMUSERDATA/$1/config/localconfig.vdf" | cut -f 5
}

get_login() {
	grep -B 2 "`get_ID64 "$1"`" "$STEAMDIR"/config/config.vdf | head -n 1 | awk '{ print $1 }'
}

get_ID3() {
	echo "[U:1:$1]"
}

get_ID64() {
	expr 76561197960265728 + $1
}

for accpath in "$STEAMUSERDATA"/*; do
	[ -d $accpath ] || continue
	acc=`basename "$accpath"`
	echo -e "  ID3:\t\t\t`get_ID3 "$acc"`"
	echo -e "    Login:\t\t`get_login "$acc"`"
	echo -e "    Name:\t\t`get_name "$acc"`"
	echo -en "    CS:GO config:\t"
	if [ -e "$accpath"/730 ]; then
		if [ -L "$accpath"/730 ]; then
			cspath="`readlink "$accpath"/730`"
			csacc=$(basename "`readlink -f "$accpath/$cspath.."`")
			echo "Linked to `get_name "$csacc"` `get_ID3 "$csacc"`"
		else
			echo "Own"
		fi
	else
		echo "No profile found"
	fi
	echo
done
