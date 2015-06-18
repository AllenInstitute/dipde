set -o verbose

# Set up
PYTHONPATH=''
CONDA_DIR=/tmp/dipde_test

conda create --file requirements.txt --prefix=$CONDA_DIR -y
	source activate $CONDA_DIR
	python setup.py test
	source deactivate
conda remove --all --prefix=$CONDA_DIR -y

