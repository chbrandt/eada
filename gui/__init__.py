__author__ = 'chbrandt'

import sys
from PySide.QtGui import QApplication,QDialog

class Form(QDialog):
    """
    """
    def __init__(self,parent=None):
        super(Form,self).__init__(parent)
        self.setWindowTitle("MyMainWindow\o/")


def main():
    app = QApplication(sys.argv)

    form = Form()
    form.show()

    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()