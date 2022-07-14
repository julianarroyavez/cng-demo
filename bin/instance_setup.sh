sudo apt-get update

sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev

curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

export PATH="/home/hygge-ev-user/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv versions
pyenv install 3.9.2
pyenv global 3.9.2
pyenv versions

sudo apt install libpq-dev

pip install virtualenv

virtualenv .venv_hygge_ev_app

source .venv_hygge_ev_app/bin/activate

pip install -r requirements.txt

deactivate