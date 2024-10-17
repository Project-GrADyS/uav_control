# bash register_protcol.sh <protocol_name> <protocol_path>
# protocol path must be in python module path standart

ls ~/.config

if ! -d "~/.config/gradys"
then
    mkdir ~/.config/gradys
fi
if ! -f "~/.config/gradys/protocol.txt"
then
    echo "ALOOU"
    touch ~/.config/gradys/protocol.txt
fi
echo "$1 $2" >> ~/.config/gradys/protocol.txt