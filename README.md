# Magic happens
docker run -it --rm -v `pwd`:/code --entrypoint "/bin/bash" ecs251
alias spm="poetry run python spm/__main__.py"

1. Build the containers: docker-compose build or docker-compose up --force-recreate --build
2. Run ./demo.sh In tmux run the command ':select-layout tiled' (prefix I think ctrl b by default)
3. In one of the "user" containers, run "spm bootstrap"
4. Run "spm tree" in the others to confirm it works!