if [[ ! "~/.condig/ardupilot" ]]
then
    mkdir ~/.config/ardupilot
fi
echo "$1=$2,$3,$4,$5" >> ~/.config/ardupilot/locations.txt