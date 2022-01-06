import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPainter

from Ui_main import *
from functools import partial
from database_operate import *
from PyQt5.QtWidgets import *

opr = DatabaseOperate("104.168.172.47", "forfind", "000000", "exercise")
pd.set_option('display.max_columns', None,
              'display.max_rows', None,
              'display.max_colwidth', None,
              'display.width', 100,
              'expand_frame_repr', False)

def test(ui):
    cata = ''
    print("succ")
    cata = "'" + ui.ctt_1.toPlainText() + "'"

    print(cata)


def add(ui):
    chap = int(ui.para1.text())
    sec = int(ui.para2.text())
    cata = ''
    diff = ''
    if ui.cata_1.isChecked():
        cata = "'选择'"
    if ui.cata_2.isChecked():
        cata = "'判断'"
    if ui.cata_3.isChecked():
        cata = "'填空'"
    if ui.cata_4.isChecked():
        cata = "'名词解释'"
    if ui.cata_5.isChecked():
        cata = "'问答'"
    if ui.cata_6.isChecked():
        cata = "'算法'"
    if ui.cata_7.isChecked():
        cata = "'计算'"
    if ui.diff_1.isChecked():
        diff = "'低'"
    if ui.diff_2.isChecked():
        diff = "'高'"
    if ui.diff_3.isChecked():
        diff = "'中'"

    ques = "'" + ui.ctt_1.toPlainText() + "'"
    ans = "'" + ui.ctt_2.toPlainText() + "'"
    ui.ctt_1.clear()
    ui.ctt_2.clear()
    print("章：", chap, "节:", sec, "类别:", cata, "难度:", diff)
    print("题目", ques, "答案", ans)
    global opr

    print(cata)
    opr.add_exercise(ques, "null", ans, "null", cata, chap, sec, diff)
    d = opr.query_exercise("category="+cata)
    print(d)

def sreach(ui):
    global opr
    pd.set_option('display.max_columns', None,
              'display.max_rows', None,
              'display.max_colwidth', None,
              'display.width', 100,
              'expand_frame_repr', False)
    value = ui.inputtxt.toPlainText()
    if ui.keybtn.isChecked():
        by = 0
    if ui.codebtn.isChecked():
        d = opr.query_exercise("exercise_base_info.ExerciseCode="+value)
        print(d)
    if ui.catabtn.isChecked():
        cata = "'"+value+"'"
        d = opr.query_exercise("category="+cata)
        print(d)
    print(d[["ExerciseCode","topic","answer"]])


    ui.outputlist.clear()

    for i in range(d.shape[0]):
        ui.outputlist.addItem(str(d.at[i,"ExerciseCode"])+' '+str(d.at[i,"topic"])+' '+str(d.at[i,"answer"]))
        #print(str(d.at[i,"ExerciseCode"])+' '+str(d.at[i,"topic"])+' '+str(d.at[i,"answer"]))

def remove_item(list):
    global opr
    if list.count() > 0:
        for i in range(list.count()):
            item = list.item(i)

            if item.isSelected():
                code = int(str(list.item(i).text()).split()[0])

                print("code:",code)

                list.removeItemWidget(list.takeItem(i))
                # 此处+对话框
                global opr
                pd.set_option('display.max_columns', None,
                    'display.max_rows', None,
                    'display.max_colwidth', None,
                    'display.width', 100,
                    'expand_frame_repr', False)
                opr.delete_exercise(code)
                break
def Df2Ls(data):
    datalist = []
    for i in range(len(data)):
        datalist.append([str(data.iat[i,0]),int(data.iat[i,1])])
    return datalist

def statistic_info():
    global opr
    data = opr.statistic_exercise("difficulty")
    print(data)
    datalist = Df2Ls(data)
    print(datalist)
    return datalist

def updata_info(win):
    datalist = statistic_info()
    win.showall(datalist)

def collect_paper_info(ui):
    pass

#def create_paper_with(data):


def set_pdctview(win):
    category = opr.statistic_exercise("category")
    category_list = Df2Ls(category)
    chapter = opr.statistic_exercise("chapter")
    chapter_list = Df2Ls(chapter)

    win.set_pdctview(category_list,chapter_list)

def main():
    app = QApplication(sys.argv)
    datalist = statistic_info()
    print(datalist)
    mainwin = mainWindow(datalist)
    mainwin.show()

    mainwin.addui.submit.clicked.connect(partial(add, mainwin.addui))
    mainwin.schui.schbtn.clicked.connect(partial(sreach, mainwin.schui))
    mainwin.schui.delbtn.clicked.connect(partial(remove_item, mainwin.schui.outputlist))
    mainwin.disbtn.clicked.connect(partial(updata_info,mainwin))
    mainwin.pdctbtn.clicked.connect(partial(set_pdctview,mainwin))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
