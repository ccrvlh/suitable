test:
	docker build -t suitable_test_image . && \
	docker run --rm --name suitable_runtest_instance suitable_test_image
