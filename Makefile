old_test:
	docker build --platform=linux/amd64 -t suitable_test_image . && \
	docker run --rm --name suitable_runtest_instance suitable_test_image

test:
	docker-compose up --build --force-recreate
	
