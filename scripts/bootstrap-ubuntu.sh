#!/bin/bash
# Install required dependencies

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace


# Colour vars
GN='\033[0;32m' # Green
NC='\033[0m'    # No Color

DEP_FILE="$1"

# Only add the PPA if it's not already there
if ! grep -q "^deb .*$the_ppa" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo -e "${GN}Adding python3.6 PPA${NC}"
    sudo add-apt-repository ppa:jonathonf/python-3.6
fi

apt-get update

# Allow for comments in the dep file and then install all of them through apt.
grep -v "#" "$DEP_FILE" | grep -v "^$" | xargs apt-get install -y

apt-get clean
