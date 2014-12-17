PYTHONPATH=''
conda create --file requirements.txt --prefix=`pwd`/dipde_test
source activate dipde_test
#py.test
python setup.py test
source deactivate
conda remove --all --prefix=`pwd`/dipde_test
