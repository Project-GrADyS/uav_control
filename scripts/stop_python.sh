for i in $(ps | grep "python3" | cut -c3-7); do
    $(kill "$i")
done