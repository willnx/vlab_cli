
clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel --universal

install: build
	pip install -U dist/*.whl

uninstall:
	-pip uninstall -y vlab-cli

test: uninstall install
	cd tests && nosetests -v --with-coverage --cover-package=vlab_cli
