PYTHONPATH=''
conda create -n dipde_test --file requirements.txt --prefix=`pwd`
source activate dipde_test
#py.test
python setup.py test
source deactivate
conda remove -n dipde_test --all
