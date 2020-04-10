CONFIG=$@

docker:
	docker build -t hellmuth -f etc/Dockerfile .

test:
	make docker
	docker run -it --rm --name hellmuth-test \
		-v ${PWD}/src/:/modules \
		--entrypoint=/home/hellmuth/test.py hellmuth

%:
	make docker
	docker run -it --rm --name hellmuth-$(CONFIG) \
		-v ${PWD}/cfg/$(CONFIG)/:/state \
		-v ${PWD}/src/:/modules hellmuth


