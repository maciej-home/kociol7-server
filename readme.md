## Install

### SQL
```bash
su - postgres
createuser --pwprompt kociol7
createdb --owner=kociol7 kociol7
```

### Server
```bash
git clone https://github.com/maciej-home/kociol7-server
cd kociol7-server
chmod +x ./main.py
pip install -r requirements.txt
```
Edit `config.py` file adjusting to your needs
If using `systemd`:
```bash
sudo cp kociol7.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kociol7 --now
```
