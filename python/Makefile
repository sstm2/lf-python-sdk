VERSION ?= patch

release:
	bump2version $(VERSION) --allow-dirty
	git push origin main --tags
