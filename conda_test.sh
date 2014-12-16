PYTHONPATH=''
yes | conda create -n dipde_test --file requirements.txt
source activate dipde_test
#py.test
python setup.py test
source deactivate
yes | conda remove -n dipde_test --all
