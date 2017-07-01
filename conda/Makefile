BUILD_DIR=build
PYTHON2_BUILD_DIR=$(BUILD_DIR)/python2_build
PYTHON3_BUILD_DIR=$(BUILD_DIR)/python3_build
DEPLOY_DIR=$(BUILD_DIR)/deploy
NUMBER=3

DIRS=$(DEPLOY_DIR)/linux-32 $(DEPLOY_DIR)/osx-64 \
	$(DEPLOY_DIR)/win-32 $(DEPLOY_DIR)/win-64 \
	$(PYTHON2_BUILD_DIR)/linux-64 $(PYTHON3_BUILD_DIR)/linux-64

OBJS=$(wildcard $(DIRS:=/*tar.bz2))

clean:
	rm -fr $(BUILD_DIR)

build2:
	mkdir -p $(PYTHON2_BUILD_DIR)
	conda config --set anaconda_upload no
	conda build --output-folder $(PYTHON2_BUILD_DIR) --python 2.7 . 

build3:
	mkdir -p $(PYTHON3_BUILD_DIR)
	conda config --set anaconda_upload no
	conda build --output-folder $(PYTHON3_BUILD_DIR) --python 3.6 .

build: build2 build3

convert2:
	mkdir -p  $(DEPLOY_DIR)
	conda convert ./$(PYTHON2_BUILD_DIR)/linux-64/dipde-0.2.1-py27_$(NUMBER).tar.bz2 -p all -o $(DEPLOY_DIR)

convert3:
	mkdir -p  $(DEPLOY_DIR)
	conda convert ./$(PYTHON3_BUILD_DIR)/linux-64/dipde-0.2.1-py36_$(NUMBER).tar.bz2 -p all -o $(DEPLOY_DIR)

convert: convert2 convert3

deployment:
	for i in $(OBJS); do \
		anaconda upload --force $$i; \
	done

all: clean build convert