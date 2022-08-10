# This will run all of the tests in containers (1 as the source machine, 2 for target hosts)
test:
	docker-compose -f ./servers/docker-compose.yml up --build --force-recreate
	

# This will build two containers for local testing with Pytest
test_local:
	docker-compose -f ./servers/docker-compose-local.yml up --build --force-recreate
	
