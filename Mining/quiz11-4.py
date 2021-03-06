### Q4 : GIF 처리 기능 추가(RGB) ###

from tkinter import *
import os.path
import math
from  tkinter.filedialog import *
from  tkinter.simpledialog import *
import threading
import struct
import sqlite3
import csv
import pymysql
from xlsxwriter import Workbook
import xlrd
import numpy as np

## 함수 선언부
def loadImage(fname) :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH, photo
    global inImageR, inImageG, inImageB, outImageR, outImageG, outImgageB
    photo = PhotoImage(file=filename)
    inW = photo.width()
    inH = photo.height()
    inImage = []
    tmpList = []
    for i in range(inH):
        tmpList = []
        for k in range(inW) :
            tmpList.append(np.array([0, 0, 0]))  #RGB를 각각 0 벡터를 만들어 inImage에 인덱스 형성
        inImage.append(tmpList)
    for  i  in range(inH):
        for  k  in  range(inW):
            r, g, b = photo.get(k, i)
            inImage[i][k] = [r, g, b] #RGB를 각각 리스트로 넣어 inImage에 추가
    inImage = np.array(inImage)
    photo = None

def openFile() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("GIF파일", "*.gif; *.png"), ("모든파일", "*.*")))
    loadImage(filename) # 파일 --> 입력메모리
    equal() # 입력메모리--> 출력메모리

def display() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # 기존에 캐버스 있으면 뜯어내기.
    if  canvas != None :
        canvas.destroy()
    # 화면 준비 (고정됨)
    VIEW_X, VIEW_Y = 128, 128
    if VIEW_X >= outW or VIEW_Y >= outH:
        VIEW_X = outW
        VIEW_Y = outH
    step = int(outW / VIEW_X) # 축소배수
    window.geometry(str(VIEW_X*2) + 'x' + str(VIEW_Y*2))
    canvas = Canvas(window, width=VIEW_X, height=VIEW_Y)
    paper = PhotoImage(width=VIEW_X, height=VIEW_Y)
    canvas.create_image((VIEW_X/2, VIEW_Y/2), image=paper, state='normal')
    # 화면에 출력
    def putPixel() :
        for i in range(0, outH, step) :
            for k in range(0, outW, step) :
                data = outImage[i][k]
                paper.put('#%02x%02x%02x' % (int(data[0]), int(data[1]), int(data[2])), (int(k/step), int(i/step)))
    threading.Thread(target=putPixel).start()
    canvas.pack(expand=1, anchor=CENTER)
    status.configure(text="이미지 정보: " + str(outW) + " X " + str(outH))
    status.pack()

def equal() :  # 동일 영상 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH, photo
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):
        tmpList = []
        for k in range(outW):
            tmpList.append(np.array([0, 0, 0])) # RGB 0행렬
        outImage.append(tmpList)        
    for  i  in  range(inH):
        for  k  in  range(inW):
            outImage[i][k] = inImage[i][k]
    outImage = np.array(outImage)
    display()

def addImage() :  # 밝게하기 알고리즘
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    outW = inW
    outH = inH
    outImage = []
    tmpList = []
    for i in range(outH):
        tmpList = []
        for k in range(outW):
            tmpList.append(np.array([0, 0, 0]))
        outImage.append(tmpList)
    outImage = np.array(outImage)
    brt = askinteger('밝게하기', '밝게할 값', minvalue=1, maxvalue=255)
    inImage = np.array(inImage)
    for  i  in  range(inH) :
        for  k  in  range(inW) :
            outImage[i][k] = inImage[i][k] + brt # numpy broadcasting을 이용한 빠른 RGB 연산
            outImage[i][k][outImage[i][k] > 255] = 255
            outImage[i][k][outImage[i][k] < 0] = 0
    display()

def saveFile() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    saveFp = asksaveasfile(parent=window, mode='wb',
                               defaultextension="*.gif", filetypes=(("GIF파일", "*.gif"), ("모든파일", "*.*")))
    for i in range(outW):
        for k in range(outH):
            saveFp.write( struct.pack(outImage[i][k][0], outImage[i][k][1], outImage[i][k][2]))
    saveFp.close()

def exitFile() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    pass

def saveCSV() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    output_file = asksaveasfile(parent=window, mode='w',
                               defaultextension="*.csv", filetypes=(("CSV파일", "*.csv"), ("모든파일", "*.*")))
    output_file = output_file.name

    header = ['Column', 'Row', 'Value']
    with open(output_file, 'w', newline='') as filewriter:
        csvWriter = csv.writer(filewriter)
        csvWriter.writerow(header)
        for row in range(outW):
            for col in range(outH):
                data = outImage[row][col]
                row_list = [row, col, data]
                csvWriter.writerow(row_list)
    print('OK!')

def saveShuffleCSV() :
    pass

def loadCSV(fname) :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    fsize = -1
    fp = open(fname, 'r')
    for  f  in fp :
        fsize += 1
    fp.close()
    inH = inW = int(math.sqrt(fsize))  # 입력메모리 크기 결정! (중요)
    inImage = []; tmpList = []
    for i in range(inH) :  # 입력메모리 확보(0으로 초기화)
        tmpList = []
        for k in range(inW) :
            tmpList.append(0)
        inImage.append(tmpList)
    # 파일 --> 메모리로 데이터 로딩
    fp = open(fname, 'r') # 파일 열기(바이너리 모드)
    csvFP = csv.reader(fp)
    next(csvFP)
    for row_list in csvFP:
        row= int(row_list[0])
        col = int(row_list[1])
        value = row_list[2][1:-1].split() # string 상태의 RGB LIST를 다시 LIST 형태로 변환
        value = np.array(value, dtype=np.int32) # string을 int32으로 타입 변환
        inImage[row][col] = value
    fp.close()

def openCSV() :
    global window, canvas, paper, filename,inImage, outImage,inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("CSV파일", "*.csv"), ("모든파일", "*.*")))
    loadCSV(filename) # 파일 --> 입력메모리
    equal() # 입력메모리--> 출력메모리

def saveSQLite() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global csvList, input_file
    con = sqlite3.connect('d:/data/imageDB2')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    # 열이름 리스트 만들기
    inImage = outImage.copy()
    fname = os.path.basename(filename).split(".")[0]
    try:    
        sql = "DELETE FROM imageTable WHERE filename = '" + fname + "'"
        cur.execute(sql)
    except: pass
    try:
        sql = "CREATE TABLE imageTable(filename CHAR(20), resolution smallint" + \
            ", row  smallint,  col  smallint, value CHAR(20))"
        cur.execute(sql)
        con.commit()
    except:
        pass
    for i in range(inW) :
        for k in range(inH) :
            sql = "INSERT INTO imageTable VALUES('" + fname + "'," + str(inW) + \
                "," + str(i) + "," + str(k) + "," + "'" + str(inImage[i][k]) + "'" +")"
            cur.execute(sql) # str은 ' ' 앞뒤로 중요 (query)
    con.commit()
    cur.close()
    con.close()  # 데이터베이스 연결 종료
    print('Ok!')
    
def loadSQLite():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    con = sqlite3.connect('d:/data/imageDB2')  # 데이터베이스 지정(또는 연결)
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    inImage = []
    try:    
        sql = "SELECT DISTINCT filename, resolution FROM imageTable"
        cur.execute(sql)
        tableNameList = []
        while True :
            row = cur.fetchone()
            if row == None:
                break
            tableNameList.append(row[0] + ":" + str(row[1]))
        ##    
        def selectTable() :
            global window, filename, inImage, inW, inH, outW, outH
            index = listbox.curselection()[0]
            subWindow.destroy()
            fname, res = tableNameList[index].split(':')
            filename = fname
            sql = "SELECT * FROM imageTable WHERE filename = " + "'" + fname + "'"
            cur.execute(sql)
            row = cur.fetchone()
            inW = inH = int(row[1])
            tmpList = []
            for i in range(inH) :
                tmpList = []
                for k in range(inW) :
                    tmpList.append([0, 0, 0])
                inImage.append(tmpList)
            for i in range(inW*inH):
                inImage[int(row[2])][int(row[3])] = row[4][1:-1].split() # str을 다시 list로 (rgb)
                row = cur.fetchone()
            inImage = np.array(inImage, dtype=np.int32)
            cur.close()
            con.close()
            equal()    
        ##   
        subWindow = Toplevel(window)
        listbox = Listbox(subWindow)
        button = Button(subWindow, text='선택', command=selectTable)
        listbox.pack()
        button.pack()
        for  sName in tableNameList :
            listbox.insert(END, sName)
        subWindow.lift()
            ##
    except:
        cur.close()
        con.close()
        print("error")
        ##    

## Q1 / Q1+ ##
def savemySql() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # DB쿼리 / imageDB 생성
    '''
    mysql -u root -p
    CREATE DATABASE imageDB;
    '''
    # pymysql 연결 // 리눅스 ip, user: root // imageDB
    con = pymysql.connect(host='192.168.226.131', user='root', password='1234', db='imageDB2', charset='utf8')
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    # 열이름 리스트 만들기
    inImage = outImage.copy() # *변화된 outImage를 inImage로 변환
    fname = os.path.basename(filename).split(".")[0]
    sql = "DELETE FROM imageTable WHERE filename = '" + fname + "'" # 기존 데이터 삭제
    try: 
#        print(sql)
        cur.execute(sql)
        con.commit() # commit 중요
    except: pass
    try:
        sql = "CREATE TABLE imageTable( filename CHAR(20), resolution smallint" + \
            ", row  smallint,  col  smallint, value  char(20))"
        cur.execute(sql)
    except:
        pass

    for i in range(inW) :
        for k in range(inH) :
            sql = "INSERT INTO imageTable VALUES('" + fname + "'," + str(inW) + \
                "," + str(i) + "," + str(k) + "," + "'" + str(inImage[i][k]) + "'" + ")"
            cur.execute(sql)
    con.commit()
    cur.close()
    con.close()  # 데이터베이스 연결 종료
    print('Ok!')
    
def loadmySql():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # pymysql 연결 // linux >> DB 연결
    con = pymysql.connect(host='192.168.226.131', user='root', password='1234', db='imageDB2', charset='utf8')
    cur = con.cursor()  # 연결 통로 생성 (쿼리문을 날릴 통로)
    inImage = []
    try:    
        # 중복치 제거 후 수집 >> distinct
        sql = "SELECT DISTINCT filename, resolution FROM imageTable"
        cur.execute(sql)
        tableNameList = []
        while True :
            row = cur.fetchone()
            if row == None:
                break
            tableNameList.append(row[0] + ":" + str(row[1]))
        ##    
        def selectTable() :
            global window, filename, inImage, inW, inH, outW, outH
            index = listbox.curselection()[0]
            subWindow.destroy()
            fname, res = tableNameList[index].split(':')
            filename = fname
            sql = "SELECT * FROM imageTable WHERE filename = " + "'" + fname + "'"
            cur.execute(sql)
            row = cur.fetchone()
            inW = inH = int(row[1])
            tmpList = []
            for i in range(inH) :
                tmpList = []
                for k in range(inW) :
                    tmpList.append(0)
                inImage.append(tmpList)
            for i in range(inW*inH):
                # ROW = [filename, resolution, rownum, colnum, grayscale]
                inImage[int(row[2])][int(row[3])] = row[4][1:-1].split()
                row = cur.fetchone()
            np.array(inImage, dtype=np.int32)
            cur.close()
            con.close()
            equal()    
        ##   
        subWindow = Toplevel(window)
        listbox = Listbox(subWindow)
        button = Button(subWindow, text='선택', command=selectTable)
        listbox.pack()
        button.pack()
        for  sName in tableNameList :
            listbox.insert(END, sName)
        subWindow.lift()
            ##
    except:
        cur.close()
        con.close()
        print("error")
        
## Q2 ##        
def sqlExcel1():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    # save할 파일 결정
    outfilename = asksaveasfile(parent=window, mode='wb',
                               defaultextension="*.xlsx", filetypes=(("xlsx파일", "*.xlsx"), ("모든파일", "*.*")))
    wb = Workbook(outfilename)
    ws = wb.add_worksheet(os.path.basename(filename))
    with open(filename, 'rb') as fReader:
        for i in range(inW):
            for j in range(inH):
                data = inImage[i][j] # 저장되어 있던 inImage에서 data 추출
                ws.write(i, j, str(data)) # index마다 쓰기
    wb.close()
    
    

def sqlExcel2():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    outfilename = asksaveasfile(parent=window, mode='wb',
                               defaultextension="*.xlsx", filetypes=(("xlsx파일", "*.xlsx"), ("모든파일", "*.*")))
    wb = Workbook(outfilename)
    ws = wb.add_worksheet(os.path.basename(filename))
    with open(filename, 'rb') as fReader:
        # 워크시트의 열 너비 / 행 높이 지정
        ws.set_column(0, inW, 1.0) # 0.34
        for row in range(inH):
            ws.set_row(row, 9.5) # 0.35
        for i in range(inW):
            for j in range(inH):
                data = inImage[i][j] # 기존에 있던 inImage에서 출력
                # data 셀 배경색 지정 #000000~FFFFFF
                if data[0] <= 15: # 15 이하일 경우, 1자리 수이기 때문에 0을 추가
                    hexStr = '#' + ('0' + hex(data[0])[2:])
                else: 
                    hexStr = '#' + (hex(data[0])[2:]) # 16진수 변환 후, R(2자리)
                if data[1] <= 15:
                    hexStr += ('0' + hex(data[1])[2:]) # G(2자리)
                else:
                    hexStr += hex(data[1])[2:]
                if data[2] <= 15:
                    hexStr += ('0' + hex(data[2])[2:]) # B(2자리)
                else:
                    hexStr += hex(data[2])[2:]
                cell_format = wb.add_format() # RGB코드는 #을 앞에
                cell_format.set_bg_color(hexStr)
                ws.write(i, j, '', cell_format)
    wb.close()

def sqlExcel3() :
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    inImage = []
    input_file = askopenfilename(parent=window, filetypes=(("EXCEL파일", "*.xls;*.xlsx"), ("모든파일", "*.*")))
    workbook = xlrd.open_workbook(input_file)
    sheetCount = workbook.nsheets
    for sheet in workbook.sheets():
        sRow = sheet.nrows
        sCol = sheet.ncols
        for i in range(sRow):
            tmpList = []
            for j in range(sCol):
                value = sheet.cell_value(i, j)[1:-1].split()
                tmpList.append(value)
            inImage.append(tmpList)
    np.array(inImage, dtype=np.int32)
    inW = len(inImage)
    inH = len(inImage[0])
    equal()

## 전역 변수부
window, canvas, paper, filename = [None] * 4
inImage, outImage = [], []; inW, inH, outW, outH = [0] * 4
panYN = False;  sx, sy, ex, ey = [0] * 4
VIEW_X, VIEW_Y = 128, 128

## 메인 코드부
window = Tk();  window.geometry('200x200');
window.title('영상 처리&데이터 분석 Ver 0.4')
status = Label(window, text='이미지 정보: ', bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)

mainMenu = Menu(window);window.config(menu=mainMenu)
fileMenu = Menu(mainMenu);mainMenu.add_cascade(label='파일', menu=fileMenu)
fileMenu.add_command(label='열기', command=openFile)
fileMenu.add_command(label='저장', command=saveFile)
fileMenu.add_separator()
fileMenu.add_command(label='종료', command=exitFile)

pixelMenu = Menu(mainMenu);mainMenu.add_cascade(label='화소점처리', menu=pixelMenu)
pixelMenu.add_command(label='동일영상', command=equal)
pixelMenu.add_command(label='밝게하기', command=addImage)

otherMenu = Menu(mainMenu);mainMenu.add_cascade(label='다른 포맷 처리', menu=otherMenu)
otherMenu.add_command(label='CSV로 내보내기', command=saveCSV)
otherMenu.add_command(label='CSV(셔플)로 내보내기', command=saveShuffleCSV)
otherMenu.add_command(label='CSV 불러오기', command=openCSV)
otherMenu.add_separator()
otherMenu.add_command(label='SQLite로 내보내기', command=saveSQLite)
otherMenu.add_command(label='SQLite 목록 불러오기', command=loadSQLite)
otherMenu.add_separator()
otherMenu.add_command(label='mySQL로 내보내기', command=savemySql)
otherMenu.add_command(label='mySQL 목록 불러오기', command=loadmySql)
otherMenu.add_separator()
otherMenu.add_command(label='Excel로 내보내기(숫자)', command=sqlExcel1)
otherMenu.add_command(label='Excel로 내보내기(음영)', command=sqlExcel2)
otherMenu.add_command(label='Excel로 불러오기(숫자)', command=sqlExcel3)


window.mainloop()
