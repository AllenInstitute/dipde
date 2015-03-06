PROJECTNAME = dipde
VERSION = 0
RELEASE = 1
REVISION = 1
DISTDIR = dist
BUILDDIR = build
RELEASEDIR = $(PROJECTNAME)-$(VERSION).$(RELEASE).$(REVISION)
EGGINFODIR = $(PROJECTNAME).egg-info
DOCDIR = doc

setversion:
	sed -i.bak 's/'\''[0-9]\+.[0-9]\+.[0-9]\+'\''/'\''${VERSION}.${RELEASE}.${REVISION}'\''/g' $(PROJECTNAME)/__init__.py

build:
	mkdir -p $(DISTDIR)/$(PROJECTNAME)
	cp -r $(PROJECTNAME) setup.py README.md $(DISTDIR)/$(PROJECTNAME)/
	cd $(DISTDIR); tar czvf $(PROJECTNAME).tgz $(PROJECTNAME)
	

distutils_build: clean
	python setup.py build

sdist: distutils_build
	python setup.py sdist
	
doc: clean
	sphinx-apidoc -d 4 -H "$(PROJECTNAME)" -A "Allen Institute for Brain Science" -V $(VERSION) -R $(VERSION).$(RELEASE).${REVISION} --full -o doc $(PROJECTNAME)
	cp doc_template/*.rst doc_template/conf.py doc	
	sed -ie "s/|version|/${VERSION}.${RELEASE}.${REVISION}/g" doc/user.rst
	cd doc && make html || true

clean:
	rm -rf $(DISTDIR)
	rm -rf $(BUILDDIR)
	rm -rf $(RELEASEDIR)
	rm -rf $(EGGINFODIR)
	rm -rf $(DOCDIR)