.PHONY: build compile components clean stylus

build: components stylus
	@component build --dev -o ../june/public/static -n app

components: component.json
	@component install --dev

compile: components stylus
	@component-build -o ../june/public/static -n app -p .

clean:
	rm -fr build components node_modules

stylus:
	@stylus index.styl -I stylus -I node_modules
