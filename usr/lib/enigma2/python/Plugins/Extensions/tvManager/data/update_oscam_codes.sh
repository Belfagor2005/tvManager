#!/bin/bash
#### "***********************************************"
#### "*                 Created By Levi45            *"
#### "***********************************************"

# Configuration
OSCAM_FILE="/etc/tuxbox/config/oscam.server"
BACKUP_DIR="/tmp/oscam_backups"
BACKUP_FILE="$BACKUP_DIR/oscam.server.backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/tmp/oscam_update.log"
TEMP_FILE="/tmp/oscam_temp"
KEYS_URL="https://raw.githubusercontent.com/levi-45/tivusatrsakey/main/rsakey_tiger.txt"

# Hardcoded keys
CURRENT_KEYS=$(cat << 'EOF'
rsakey                        = A22DE56CA2560B596E4B76DDFD1CFE7528F696E229B3A88B60CE6250287FBC0F62F62485D3FD8DA69B2C3C5B8A9E859608BB56169A0445180951D9F85EBC4D3EFA7F3B6181DDA069D6657B38A79784CD63AB8BAE9B9CADB48632E86600D7FC5D
rsakey_tiger                  = A22DE56CA2560B596E4B76DDFD1CFE7528F696E229B3A88B60CE6250287FBC0F62F62485D3FD8DA69B2C3C5B8A9E859608BB56169A0445180951D9F85EBC4D3EFA7F3B6181DDA069D6657B38A79784CD63AB8BAE9B9CADB48632E86600D7FC5D
tiger_save_emm                = 0
EOF
)

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to download new keys
download_new_keys() {
    log "Downloading new keys from: $KEYS_URL"
    if wget -q --timeout=30 -O "/tmp/new_tivusat_keys.txt" "$KEYS_URL"; then
        if [ -s "/tmp/new_tivusat_keys.txt" ] && grep -q "rsakey" "/tmp/new_tivusat_keys.txt"; then
            log "New keys downloaded successfully"
            cat "/tmp/new_tivusat_keys.txt"
            return 0
        fi
    fi
    log "Failed to download new keys"
    return 1
}

# Function to get hardcoded keys
get_hardcoded_keys() {
    echo "$CURRENT_KEYS"
}

# Function to check if Tivusat reader exists
get_tivusat_reader_info() {
    awk '
    /^\[reader\]/ {
        in_reader=1
        reader_start=NR
        has_tivusat_label=0
        has_183e=0
    }
    in_reader {
        if (/label.*Tivusat/) has_tivusat_label=1
        if (/caid.*183E/) has_183e=1
        if (/^\[/ && NR > reader_start) {
            if (has_tivusat_label && has_183e) {
                print reader_start
                exit
            }
            in_reader=0
        }
    }
    END {
        if (in_reader && has_tivusat_label && has_183e) {
            print reader_start
        }
    }
    ' "$OSCAM_FILE"
}

# Caso 1: Update existing Tivusat reader
update_existing_reader() {
    local start_line="$1"
    local new_keys="$2"
    log "Updating existing Tivusat reader..."
    
    local end_line=$(awk -v start="$start_line" 'NR > start && /^\[reader\]/ { print NR-1; exit } END { print NR }' "$OSCAM_FILE")
    
    awk -v start="$start_line" -v end="$end_line" -v new_keys="$new_keys" '
    BEGIN {
        split(new_keys, key_lines, "\n")
        in_target=0
        processed=0
    }
    {
        if (NR < start) {
            print
            next
        }
        if (NR == start) {
            in_target=1
            print
            next
        }
        if (in_target && !processed) {
            if (/rsakey[[:space:]]*=/ || /tiger_/) {
                next
            }
            if (!/rsakey[[:space:]]*=/ && !/tiger_/ && !/^[[:space:]]*$/) {
                for (i in key_lines) {
                    if (key_lines[i] != "") print key_lines[i]
                }
                processed=1
            }
            print
            next
        }
        print
    }
    END {
        if (in_target && !processed) {
            for (i in key_lines) {
                if (key_lines[i] != "") print key_lines[i]
            }
        }
    }
    ' "$OSCAM_FILE" > "${TEMP_FILE}_updated"
    
    mv "${TEMP_FILE}_updated" "$OSCAM_FILE"
}

# Caso 2: Convert existing reader to Tivusat
convert_to_tivusat_reader() {
    local start_line="$1"
    local new_keys="$2"
    log "Converting reader to Tivusat..."
    
    local end_line=$(awk -v start="$start_line" 'NR > start && /^\[reader\]/ { print NR-1; exit } END { print NR }' "$OSCAM_FILE")
    
    local new_reader="#################################################################
####################### Levi45 Protocol  ########################
#################################################################

[reader]
label                         = Tivusat-183E
description                   = Tivusat
protocol                      = internal
device                        = /dev/sci0
localcards                    = 183E:000000,005411
caid                          = 183E
$new_keys
detect                        = cd
nagra_read                    = 1
mhz                           = 500
ident                         = 183E:000000,005411
group                         = 1
emmcache                      = 0,3,2,0
ecmwhitelist                  = 91
ecmheaderwhitelist            = 80308ED387,81308ED387

"
    
    awk -v start="$start_line" -v end="$end_line" -v new_reader="$new_reader" '
    NR < start { print }
    NR == start { print new_reader }
    NR > end { print }
    ' "$OSCAM_FILE" > "${TEMP_FILE}_updated"
    
    mv "${TEMP_FILE}_updated" "$OSCAM_FILE"
}

# Caso 3: Create new Tivusat reader
create_new_tivusat_reader() {
    local new_keys="$1"
    log "Creating new Tivusat reader..."
    
    local new_reader="#################################################################
####################### Levi45 Protocol  ########################
#################################################################

[reader]
label                         = Tivusat-183E
description                   = Tivusat
protocol                      = internal
device                        = /dev/sci0
localcards                    = 183E:000000,005411
caid                          = 183E
$new_keys
detect                        = cd
nagra_read                    = 1
mhz                           = 500
ident                         = 183E:000000,005411
group                         = 1
emmcache                      = 0,3,2,0
ecmwhitelist                  = 91
ecmheaderwhitelist            = 80308ED387,81308ED387

"
    
    echo "$new_reader" | cat - "$OSCAM_FILE" > "${TEMP_FILE}_new"
    mv "${TEMP_FILE}_new" "$OSCAM_FILE"
}

# Main update function
update_tivusat_system() {
    local new_keys="$1"
    log "Checking Tivusat reader status..."
    
    cp "$OSCAM_FILE" "$BACKUP_FILE"
    
    local tivusat_line=$(get_tivusat_reader_info)
    
    if [ -n "$tivusat_line" ]; then
        log "Found Tivusat reader at line: $tivusat_line"
        update_existing_reader "$tivusat_line" "$new_keys"
    else
        local caid_183e_line=$(grep -n "caid.*183E" "$OSCAM_FILE" | head -1 | cut -d: -f1)
        if [ -n "$caid_183e_line" ]; then
            log "Found reader with caid 183E at line: $caid_183e_line"
            convert_to_tivusat_reader "$caid_183e_line" "$new_keys"
        else
            log "No reader found - creating new one"
            create_new_tivusat_reader "$new_keys"
        fi
    fi
}

# Main script
main() {
    log "Starting OSCam Tivusat Update..."
    mkdir -p "$BACKUP_DIR"
    
    local CURRENT_KEYS
    if download_new_keys; then
        CURRENT_KEYS=$(cat "/tmp/new_tivusat_keys.txt")
        log "Using downloaded keys"
    else
        CURRENT_KEYS=$(get_hardcoded_keys)
        log "Using hardcoded keys"
    fi
    
    if [ ! -f "$OSCAM_FILE" ]; then
        log "Error: $OSCAM_FILE not found!"
        exit 1
    fi
    
    update_tivusat_system "$CURRENT_KEYS"
    
    chmod 644 "$OSCAM_FILE"
    log "Script completed successfully"
    echo "Backup: $BACKUP_FILE"
    echo "Log: $LOG_FILE"
    
    if pgrep -x "oscam" > /dev/null; then
        pkill -x oscam
        sleep 2
        oscam -b -c /etc/tuxbox/config &
        log "OSCam restarted"
    fi
}

main "$@"