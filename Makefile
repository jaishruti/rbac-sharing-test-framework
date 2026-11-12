.PHONY: setup test report demo-bug

setup:
	pip install -r requirements.txt --break-system-packages

test:
	mkdir -p reports
	python -m pytest --junitxml=reports/junit.xml -q ; \
	python tools/report.py reports/junit.xml reports/report.html

demo-bug:
	DEMO_BUG=1 $(MAKE) test
