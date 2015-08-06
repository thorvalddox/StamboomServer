__author__ = 'thorvald'

import os

if __name__ == "__main__":
    os.chdir("../")
    import StamboomServer
    StamboomServer.app.run()