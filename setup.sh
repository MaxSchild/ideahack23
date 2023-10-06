DIR="$( cd "$( dirname "$0" )" && pwd )"
python3 -m venv $DIR
. $DIR/bin/activate
pip install -r requirements.txt
