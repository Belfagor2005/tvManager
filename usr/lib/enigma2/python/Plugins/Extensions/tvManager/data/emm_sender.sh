#!/bin/bash

# This script downloads hwemm for prov 183E from @teuta and sends it to the card
clear
oscam_version_file=$(find /tmp/ -name oscam.version | sed -n 1p)
oscam_config_dir=$(grep -ir "ConfigDir" $oscam_version_file | awk -F ":      " '{ print $2 }')
oscam_httpuser=$(grep -ir "httpuser" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
oscam_httppwd=$(grep -ir "httppwd" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
oscam_httpport=$(grep -ir "httpport" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
port=$(echo $oscam_httpport | sed -e 's|+||g')
protocol=$(if echo $oscam_httpport | grep + >/dev/null; then echo "https"; else echo "http"; fi)

# edit lululla
# ip='127.0.0.1'
ip=$(ifconfig eth0 | awk '/inet / { print $2 }' | sed -e s/addr://)
#end edit lululla 

caid='183E'
atr_183e='3F FF 95 00 FF 91 81 71 FE 47 00 54 49 47 45 52 36 30 31 20 52 65 76 4D 38 37 14'
# atr_183d='3F FF 95 00 FF 91 81 71 FF 47 00 54 49 47 45 52 30 30 33 20 52 65 76 32 35 30 64'

if ! test $oscam_version_file; then echo "The file oscam.version is not in the /tmp directory. First run oscam and then this script, BYE!"; exit 0; fi

[ ! -s "$(which curl)" ] && if [ -n "$(uname -m | grep -E 'sh4|mips|armv7l')" ]; then opkg -V0 update && opkg -V0 install curl; fi
[ ! -s "$(which curl)" ] && echo "The script requires curl to work properly. Unfortunately, it was not possible to install it, BYE!" && exit 0

# cmnd=$(curl -s -k --user ${oscam_httpuser}":"${oscam_httppwd}" --anyauth "$protocol://$ip:$port/emm_running.html?label=$label&emmcaid=$caid&ep=$emm&emmfile=&action=Launch)

local_emm_file=$oscam_config_dir"emm"
remote_emm_file='http://s4aupdater.one.pl/TIVU/emm'
echo $remote_emm_file

curl -s $remote_emm_file -o $local_emm_file
curl -s --user "${oscam_httpuser}":"${oscam_httppwd}" --anyauth -k $protocol://$ip:$port/status.html | grep "Restart Reader" | sed -e 's|<TD CLASS="statuscol1"><A HREF="status.html?action=restart&amp;label=||g' | sed 's/^[ \t]*//' | awk -F "\"" '{ print ($1) }' >/tmp/active_readers.tmp

#edit lululla
loc_tmp='/tmp/emm.txt'
command='/tmp/command.sh'
cmnd1="#!/bin/sh"
cmnd2="curl -s --user "${oscam_httpuser}":"${oscam_httppwd}" --anyauth $protocol://$ip:$port/emm_running.html?label=$label&emmcaid=$caid&ep=$emm&emmfile=&action=Launch"
cmnd3="exit 0"
echo -e "$cmnd1\n$cmnd2\n$cmnd3\n" >$command
cp -rf $local_emm_file $loc_tmp
# end edit lululla

while IFS= read -r label; do
curl -s --user "${oscam_httpuser}":"${oscam_httppwd}" --anyauth -k $protocol://$ip:$port/entitlements.html?label=$label >/tmp/"$label"_entitlements.html
atr=$(cat /tmp/"$label"_entitlements.html | grep "\<TD COLSPAN=\"4\">" | awk -F "[<>]" '{ print ($7) }' | sed 's/.$//g')
if [ "$atr_183e" == "$atr" ]; then
echo "Send new emms to $label card"
while IFS= read -r emm; do
if echo $emm | grep "^82708E0000000000D3875411.\{270\}$" >/dev/null; then
# size=len $emm
# final_str=$emm[:$size - 4]
# echo $final_str
curl -s -k --user "${oscam_httpuser}":"${oscam_httppwd}" --anyauth "$protocol://$ip:$port/emm_running.html?label=$label&emmcaid=$caid&ep=$emm&emmfile=&action=Launch" >/dev/null
fi
sleep 1
done < $local_emm_file
fi
done < /tmp/active_readers.tmp
rm -rf /tmp/*.tmp /tmp/*.html
