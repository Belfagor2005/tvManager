#! /bin/bash

clear
# oscam_version_file=$(find /tmp/ -name oscam.version | sed -n 1p)
oscam_config_dir='/etc/tuxbox/config/'
atr_183e='3F FF 95 00 FF 91 81 71 FE 47 00 54 49 47 45 52 36 30 31 20 52 65 76 4D 38 37 14'
oscam_user=$(grep -ir "httpuser" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
oscam_passwd=$(grep -ir "httppwd" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
oscam_httpport=$(grep -ir "httpport" $oscam_config_dir"oscam.conf" | awk -F "=" '{ print ($2) }' | sed 's/^[ \t]*//')
oscam_port=$(echo $oscam_httpport | sed -e 's|+||g')
protocol=$(if echo $oscam_httpport | grep + >/dev/null; then echo "https"; else echo "http"; fi)
curl -s --user "${oscam_user}":"${oscam_passwd}" --anyauth -k http://127.0.0.1:$oscam_port/status.html | grep "Restart Reader" | sed -e 's|<TD CLASS="statuscol1"><A HREF="status.html?action=restart&amp;label=||g' | sed 's/^[ \t]*//' | awk -F "\"" '{ print ($1) }' >/tmp/active_readers.tmp
while IFS= read -r label; do
curl -s --user "${oscam_user}":"${oscam_passwd}" --anyauth -k http://127.0.0.1:$oscam_port/entitlements.html?label=$label >/tmp/"$label"_entitlements.html
atr=$(cat /tmp/"$label"_entitlements.html | grep "\<TD COLSPAN=\"4\">" | awk -F "[<>]" '{ print ($7) }' | sed 's/.$//g')
if [ "$atr_183e" == "$atr" ]; then
echo "Send new emms to $label card"
# oscam_port=8888
# oscam_user=oscam
# oscam_passwd=oscam
# reader=TVSAT
reader=$label
emmm=$(curl -s https://pastebin.com/raw/ZNKDRVWT)
local_emm_file='/tmp/emm.txt'
echo -e "$emmm" >$local_emm_file
curl -s -k --user $oscam_user:$oscam_passwd --anyauth "http://127.0.0.1:$oscam_port/emm_running.html?label=$reader&emmcaid=183E&ep=$emmm&action=Launch" >/dev/null
fi
done < /tmp/active_readers.tmp
rm -rf /tmp/*.tmp /tmp/*.html
exit 0