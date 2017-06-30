build :
	conda config --set anaconda_upload no
	conda build .
	conda convert `conda build . --output` -p all -o ./build

upload :
	find ./build -type f | xargs anaconda upload

all : clean build upload

clean:
	rm -rf build
	conda build purge
