#! /bin/bash

git clone https://github.com/nicain/dipde_dev.git
cd dipde_dev

if [ "$PY_VER" = "3.6" ]
then
    git checkout python3_v0.2.1    
elif [ "$PY_VER" = "2.7" ]
then
    git checkout v0.2.1    
fi

echo 'HI'
echo
echo 3$PY3K
echo 2$PY2K
echo
echo 'HI'
env

/usr/bin/xvfb-run py.test dipde/test 2> /dev/null
