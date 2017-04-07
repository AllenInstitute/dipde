git clone https://github.com/nicain/dipde_dev.git
cd dipde_dev
git checkout v0.2.1

/usr/bin/xvfb-run py.test dipde/test 2> /dev/null
