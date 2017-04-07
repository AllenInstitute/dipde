build:
	conda config --set anaconda_upload no
	conda build .

upload:
	conda config --set anaconda_upload yes
	conda build .
	conda config --set anaconda_upload no

purge:
	conda build purge
