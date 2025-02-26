.PHONY: bootstrap
bootstrap:
	uv pip install -r requirements.txt
	python -c "from notifications_utils.version_tools import copy_config; copy_config()"
	uv pip install -r requirements_for_test.txt

.PHONY: bump-utils
bump-utils:  # Bump notifications-utils package to latest version
	python -c "from notifications_utils.version_tools import upgrade_version; upgrade_version()"

.PHONY: test
test:
	ruff check .
	ruff format --check .

.PHONY: report
report:
	python report.py

.PHONY: preview
preview: report
	open index.html
