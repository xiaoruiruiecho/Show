# Build & Install

## Linux:

**Ubuntu22只有libffi7, 没有libffi6**

```bash
wget http://archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo dpkg -i libffi6_3.2.1-8_amd64.deb

pyinstaller --onefile --add-data "user.py:." --add-data "cpu.py:." --add-data "disk.py:." --add-data "gpu.py:." --add-data "ram.py:." --add-data "utils.py:." --add-data "constant.py:." show.py
sudo cp dist/show /usr/local/bin/show
sudo chown root:root /usr/local/bin/show
sudo chmod u+s,+x /usr/local/bin/show

ls -l /usr/local/bin/show  # -rwsr-xr-x
```