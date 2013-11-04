
build: components
	@component build --dev -o ../public/static -n app

components: component.json
	@component install --dev

compile:
	@component-runtime -o ../public/static -n app

clean:
	rm -fr build components template.js

.PHONY: clean
