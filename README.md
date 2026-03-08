# Build & Install

## Linux:

**Ubuntu22只有libffi7, 没有libffi6**

```bash
# to install libffi6 (if needed)
wget http://archive.ubuntu.com/ubuntu/pool/main/libf/libffi/libffi6_3.2.1-8_amd64.deb
sudo dpkg -i libffi6_3.2.1-8_amd64.deb

# build & install show tool
pyinstaller --onefile --add-data "core/user.py:." --add-data "core/cpu.py:." --add-data "core/disk.py:." --add-data "core/gpu.py:." --add-data "core/ram.py:." --add-data "core/utils.py:." --add-data "core/constant.py:." show.py
sudo cp dist/show /usr/local/bin/show
sudo chown root:root /usr/local/bin/show
sudo chmod u+s,+x /usr/local/bin/show

ls -l /usr/local/bin/show  # -rwsr-xr-x
```