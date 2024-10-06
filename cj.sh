#!/bin/bash

detect_distro() {
    case "$OSTYPE" in
        linux-android*) distro="termux" ;;
        darwin) distro="darwin" ;;
        *) distro=$(ls /etc | awk 'match($0, "(.+?)[-_](?:release|version)", groups) {if(groups[1] != "os") print groups[1}') ;;
    esac

    if [ -z "$distro" ]; then
        [ -f "/etc/os-release" ] && source /etc/os-release && distro="$ID"
        [ -z "$distro" ] && distro="invalid"
    fi
}

pause() {
    read -n1 -r -p "Press any key to continue..." key
}

banner() {
    clear
    echo -e "Introducing CJ BOMBER\nThis Bomber Was Created By CJ"
}

init_environ() {
    declare -A backends=(
        ["arch"]="pacman -S --noconfirm"
        ["debian"]="apt-get -y install"
        ["ubuntu"]="apt -y install"
        ["termux"]="apt -y install"
        ["fedora"]="yum -y install"
        ["redhat"]="yum -y install"
        ["SuSE"]="zypper -n install"
        ["sles"]="zypper -n install"
        ["darwin"]="brew install"
        ["alpine"]="apk add"
    )

    INSTALL="${backends[$distro]}"
    PYTHON="${distro}" == "termux" ? "python" : "python3"
    SUDO="$([[ "$distro" == "termux" ]] && echo "" || echo "sudo")"
    PIP="$PYTHON -m pip"
}

install_deps() {
    packages=(openssl git $PYTHON $PYTHON-pip figlet toilet)

    if [ -n "$INSTALL" ]; then
        for package in "${packages[@]}"; do
            $SUDO $INSTALL $package
        done
        $PIP install -r requirements.txt
    else
        echo "Dependencies could not be installed."
        echo "Ensure git, python3, pip3, and requirements are installed."
        exit 1
    fi
}

banner
pause
detect_distro
init_environ

if [ -f .update ]; then
    echo "All Requirements Found...."
else
    echo 'Installing Requirements....'
    install_deps
    echo "This Script Was Made By yo" > .update
    echo 'Requirements Installed....'
    pause
fi

while true; do
    banner
    echo -e " Please Read Instruction Carefully !!!\n"
    echo "Press 1 To Start SMS Bomber"
    echo "Press 2 To Start CALL Bomber (Working alla)"
    echo "Press 3 To Start MAIL Bomber (Working alla)"
    echo "Press 4 To Update the Providers List (increase messaging power)"
    echo "Press 5 To Exit"
    read -r ch
    clear

    case $ch in
        1) $PYTHON bomber.py --sms; exit ;;
        2) $PYTHON bomber.py --call; exit ;;
        3) $PYTHON bomber.py --mail; exit ;;
        4)
            echo -e "Downloading Latest Files..."
            rm -f .update
            $PYTHON bomber.py --update
            echo -e "RUN CJ BOMBER Again..."
            pause
            exit
            ;;
        5)
            banner
            exit
            ;;
        *) echo -e "Invalid Input !!!"; pause ;;
    esac
done
