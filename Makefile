clean:
	@find . -name "*.pyc" -delete

deps:
	@pip install -r test_requirements.txt

test: clean deps
	@nosetests .
