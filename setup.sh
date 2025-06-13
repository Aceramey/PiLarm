mkdir /home/$USER/alarm
mv README.md /home/$USER/alarm
mv alarm.py /home/$USER/alarm
wget -O ILI9486.py raw.githubusercontent.com/SirLefti/Python_ILI9486/main/ILI9486.py
mv ILI9486.py /home/$USER/alarm
mv clear_alarms.sh /home/$USER/alarm
mv set_alarm.py /home/$USER/alarm
mv run.sh /home/$USER/alarm
sudo dtparam spi=on
sudo apt update
sudo apt -o Acquire::Retries=5 install python3-dev libopenblas0 libfreetype6-dev libjpeg-dev zlib1g-dev fonts-liberation vlc playerctl -y
python3 -m venv /home/$USER/alarm/env
. /home/$USER/alarm/env/bin/activate
pip install --no-cache-dir pillow spidev numpy==2.0.2 rpi.gpio netifaces
echo -e '#!/bin/bash\n# rc.local\n\nsu - '"$USER"' /home/'"$USER"'/alarm/run.sh &\n\nexit 0' | sudo tee /etc/rc.local > /dev/null
echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
sudo chmod +x /etc/rc.local
rm setup.sh
echo -e "\n\n\nSetup completed! A restart is required, and upon restart, the script should run automatically :)\n\n\n"

