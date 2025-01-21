.PHONY: bootstrap
bootstrap:
	uv pip install -r requirements.txt
	python -c "from notifications_utils.version_tools import copy_config; copy_config()"
	uv pip install -r requirements_for_test.txt

.PHONY: test
test:
	ruff check .
	black --check .

.PHONY: report
report:
	python report.py

.PHONY: preview
preview: report
	open index.html
