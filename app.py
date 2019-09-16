import sys, os
sys.path.append(os.getcwd() + os.path.sep + 'python')
sys.path.append(os.getcwd() + os.path.sep)
from utils import app
from apis import *
from views import *

if __name__ == '__main__':
    app.run(threaded=True, host="0.0.0.0", port=5005)
