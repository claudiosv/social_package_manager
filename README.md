# Magic happens
docker run -it --rm -v `pwd`:/code --entrypoint "/bin/bash" ecs251
alias spm="poetry run python spm/__main__.py"
docker-compose up --force-recreate --build