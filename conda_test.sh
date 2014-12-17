PYTHONPATH=''
CONDA_DIR=`pwd`/dipde
conda create --file requirements.txt --prefix=$CONDA_DIR -y
source activate dipde_test
#py.test
python setup.py test
source deactivate
conda remove --all --prefix=$CONDA_DIR -y
