from SchedulerGui import SchedulerInterface
import sys
from PyQt5.Qt import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchedulerInterface()
    sys.exit(app.exec_())