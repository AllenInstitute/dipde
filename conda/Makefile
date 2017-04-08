build:
	conda config --set anaconda_upload no
	conda build .

upload:
	conda config --set anaconda_upload yes
	conda build .
	conda config --set anaconda_upload no
	conda convert `conda build . --output` -p all -o ./build
	find ./build -type f | xargs anaconda upload

purge:
	conda build purge
