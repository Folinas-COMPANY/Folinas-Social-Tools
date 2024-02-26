
style = """
QWidget#centralwidgetMainWindow
{
    background: #fdfdfd;
}

QProgressBar {
    border: 0;
    background-color: white;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #85C88A;
    width: 20px;
}





QCheckBox::indicator {
    border: 1px solid #747d8c;
    padding-right: 10px;
}
QCheckBox::indicator:checked {
    
    border: 1px solid #85C88A;
    background-color: #85C88A;
    
}






QToolButton{
    border: 1px solid #ced6e0;
    /* border-radius: 3px; */
    color: #2f3542;
    background: white;
}

QToolButton:hover{
    border: 0px solid #ced6e0;
    color:white;
    background: #85C88A;
}

QToolButton:disabled{
    /* border: 1px solid #ced6e0; */
    /* border-radius: 3px; */
    color: #a4b0be;
    background: #dfe4ea;
}

QPushButton{
    
    border: 1px solid #a4b0be;
    border-radius: 3px;
    color: #2f3542;
    background: white;
    padding: 6px 16px;
}


QPushButton:hover
{
    border: 0px solid #747d8c;
    color: white;
    background-color: #85C88A;
}

QPushButton:disabled
{
    
    border: 1px solid #dfe4ea;
    /* border-radius: 5px; */
    /* color: b; */
    background: #DEE1EC;
}


QTableWidget#mainProfileTable

{
    border: 1px solid #a4b0be; 
    /* border-top: 1px solid #a4b0be; */
    background-color:#EEEEEE;

}

QTableWidget#bigMainVideoTable, QTableWidget#pickAccountTableWidget

{
    border: 1px solid #a4b0be; 
    /* border-top: 1px solid #a4b0be; */
    background-color:#EEEEEE;
    /* background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #bfd9ff, stop:1 #f9ffff); */

}




QCheckBox#clearBeforeLoading{
    padding-left: 5px;
}

QTableWidget::item:selected {
    border: 0px solid #979797;
    background-color: #85C88A;
    color: #2f3542;
}



QWidget#mainWidgetCRU QLineEdit{
    border: 1px solid #ced6e0;
    border-radius: 3px;
    color: #2f3542;
    padding: 5px 12px;
}

QWidget#mainWidgetCRU QPlainTextEdit{
    border: 1px solid #ced6e0;
    border-radius: 3px;
    color: #2f3542;
    padding: 6px 16px;
}

QWidget#mainWidgetCRU QLabel{
    /* border: 1px solid #ced6e0;
    border-radius: 3px; */
    color: #2f3542;
    padding: 6px 1px;
}

QFrame#bulkAddAccounts QComboBox, QFrame#bulkAddAccounts QLineEdit, QFrame#updateDetailsVideoFrame QLineEdit {
    border: 1px solid #ced6e0;
    border-radius: 0px;
    background-color: #a4b0be;
    height: 25px;
}



QFrame#bulkAddAccounts QComboBox::drop-down {
    width: 10px;
    border-left-width: 1px;
    border-left-color: grey;
    border-left-style: #57606f;
    background-color: #57606f;
}

QFrame#bulkAddAccounts QLineEdit#lineEdit {
    height: 23px;
    border: 1px solid #ced6e0;
    background-color: #EEEEEE;
}

QFrame#bulkAddAccounts QToolButton{
    height: 20px;
    width: 20px;
}

QFrame#bulkAddAccounts QPlainTextEdit{
    border: 1px solid #ced6e0;
}

QFrame#bulkSchedule QGroupBox,QFrame#bulkEditTitle QGroupBox{
    border-radius: 3px;
    border: 1px solid #ced6e0;
}
QFrame#bulkEditTitle QLineEdit{
    border: 1px solid #ced6e0;
    border-radius: 3px;
    color: #2f3542;
    padding: 4px 6px;
}
QFrame#bulkEditTitle QPlainTextEdit{
    border: 1px solid #ced6e0;
}


"""
