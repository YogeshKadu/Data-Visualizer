import os
import numpy as np
import pandas as pd
import tkinter as tk
import matplotlib.pyplot as px
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.widgets import Slider
from tkcalendar import Calendar, DateEntry
from matplotlib.ticker import NullFormatter
from tkinter.filedialog import asksaveasfile
from matplotlib.backends.backend_pdf import PdfPages

root = tk.Tk()
root.geometry('{}x{}'.format(1200, 600))
root.title("Data Analyzer")
root.iconbitmap(r'hell.ico')

dire=None
WorkingData = None
FilteredData = None
WorkingFile = None
colList=[]
choices=['']
Order=tk.BooleanVar(root,True)
select=tk.StringVar(root)
option=tk.StringVar(root)
count = tk.IntVar(root)

def selectFolder():
	global dire
	Foldername = tk.filedialog.askdirectory(title = "Select Working Directory")
	if (Foldername != ''):
		f=open('log.txt','w')
		f.write(str(Foldername))
		f.close()
		dire = Foldername
		ShowCSV()

def MinFilter(var):
	global FilteredData
	c= None
	if (type(WorkingData) != type(c)):
		FilteredData = WorkingData[WorkingData.VarValue > float(var)]
		MiddleData()

def MaxFilter(var):
	global FilteredData
	c= None
	if (type(WorkingData) != type(c)):
		FilteredData = WorkingData[WorkingData.VarValue < float(var)]
		MiddleData()

def item_list(MiddleTable):
	_list=MiddleTable.winfo_children()
	return _list

def MiddleData():
	global FilteredData
	# FilteredData.sort_values('TimeString',axis = 0,inplace = True, na_position = 'last')
	r=1
	c=0
	for i in DataView.get_children():
		DataView.delete(i)
	index=iid=0
	DataView["show"]="headings"
	DataView.heading('#'+str(iid),text="Sr No.")
	DataView.column('#'+str(iid),stretch='yes')
	iid+=1

	for i in FilteredData.columns:
		DataView.heading('#'+str(iid),text=i)
		DataView.column('#'+str(iid),stretch='yes',minwidth=150,anchor="c")
		iid+=1
	index=iid=0
	# DataView['columns']=FilteredData.columns
	for row in FilteredData.index:
		coldata = []
		for col in FilteredData.columns:
			coldata.append(FilteredData[col][row])
		DataView.insert('',index,iid,values=coldata)
		iid=index=index+1

def SetOrder():
	global FilteredData
	if(select.get() != 'None'):
		FilteredData.sort_values(select.get(),axis = 0,ascending = Order.get(),inplace = True, na_position = 'last')
		MiddleData()

def LeftInitialise():
	global FilteredData
	wlist = item_list(OrderFrame)
	for item in wlist:
		item.destroy()
	choices = colList
	OrderTitle=tk.Label(OrderFrame,text="Order Filter")
	OrderTitle.pack(side="top",fill="x")
	select.set('None')
	ColumnList = tk.OptionMenu(OrderFrame,select,*colList)
	ColumnList.pack(side="left")
	Order.set(1)
	tk.Radiobutton(OrderFrame,text='ASC',variable=Order,value=True,width=4,command=lambda:SetOrder()).pack(side='left',ipady=5,ipadx=20,anchor = 'n')
	tk.Radiobutton(OrderFrame,text='DES',variable=Order,value=False,width=4,command=lambda:SetOrder()).pack(side='left',ipady=5,ipadx=20,anchor='n')

def OnlyCSV(dire,suffix=".csv"):
	file=os.listdir(dire)
	return [filename for filename in file if filename.endswith(suffix)]

def ShowCSV():
	if listBox.size():
		listBox.delete(0,'end')
	files = OnlyCSV(dire)
	t=0
	for i in files:
		listBox.insert(t,i)
		t+=1

def MoveData():
	global FilteredData,WorkingFile,colList,WorkingData
	if type(WorkingFile) != None:
		WorkingData = pd.read_csv(str(dire)+"/"+str(WorkingFile))
		FilteredData = WorkingData
		WorkingData = FilteredData

		FilteredData['TimeString'] = pd.to_datetime(FilteredData['TimeString'])
		WorkingData['TimeString'] = pd.to_datetime(WorkingData['TimeString'])

		colList=[]
		for col in FilteredData.columns:
			colList.append(col)
		MiddleData()
		LeftInitialise()

def GetSelectedFile(evt):
	global WorkingFile,minslider
	if listBox.size():
		index = listBox.curselection()[0]
		seltext = listBox.get(index)
		WorkingFile = str(seltext)
		MoveData()

def SetBoundry(evt):
	global FilteredData
	if (option.get() == 'Head'):
		FilteredData = WorkingData.head(int(count.get()))
	else:
		FilteredData = WorkingData.tail(int(count.get()))
		# print(count.get())
	MiddleData()

def ClearFilter():
	global FilteredData
	if type(WorkingData) != None:
		FilteredData = WorkingData
		MiddleData()

def ExportPDF():
	df = pd.DataFrame(FilteredData)
	fig, ax =plt.subplots()
	ax.axis('tight')
	ax.axis('off')
	the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
	if not(os.path.exists("Output")):
		os.mkdir("Output")
	fileNames = tk.filedialog.asksaveasfile(title = "Save File",defaultextension = '.pdf')
	if (fileNames != None):
		pp = PdfPages(str(fileNames.name))
		pp.savefig(fig, bbox_inches='tight')
		pp.close()

def ExportCSV():
	if type(FilteredData) != None:
		CSVFileDialog = tk.filedialog.asksaveasfile(title = "Save File",defaultextension = '.csv')
		FilteredData.to_csv(r''+str(CSVFileDialog.name))


def DateFilter():
	global FilteredData,WorkingData
	date = str(cal.get_date()).split('-')
	date.reverse()
	smallDate = date[0]+'/'+date[1]+'/'+date[2]+' 00:00:00'
	largeDate = date[0]+'/'+date[1]+'/'+date[2]+' 23:59:59'
	largeDate = pd.to_datetime(largeDate)
	tempWorkingData = WorkingData
	start = tempWorkingData.loc[(tempWorkingData.TimeString >= smallDate)]
	end = tempWorkingData.loc[(tempWorkingData.TimeString <= largeDate)]
	tempData = start.merge(end,sort = True,copy=True,how = 'inner')
	FilteredData = tempData
	MiddleData()

def BetweenDate():
	global FilteredData,WorkingData
	temp = str(cal1.get_date()).split('-')
	smallDate = temp[2]+'/'+temp[1]+'/'+temp[0]+' 00:00:00'
	temp = str(cal2.get_date()).split('-')
	largeDate = temp[2]+'/'+temp[1]+'/'+temp[0]+' 00:00:00'
	if(smallDate < largeDate):
		temp = smallDate
		smallDate = largeDate
		largeDate = temp
	tempWorkingData = WorkingData
	start = tempWorkingData.loc[(tempWorkingData.TimeString >= smallDate)]
	end = tempWorkingData.loc[(tempWorkingData.TimeString <= largeDate)]
	tempData = start.merge(end,sort = True,copy=True,how = 'inner')
	FilteredData = tempData
	MiddleData()


def ReturnList(data):
	temp =[]
	for i in data:
		l = str(i).split()
		temp.append(l[1])
	return temp

def MinMax(value):
	maxVal = len(value)
	lis = min(value).split(':')
	return int(maxVal), int(lis[0])

def LinePlot():
	fig, ax = plt.subplots(figsize = (12,5))
	plt.subplots_adjust(bottom=0.25)
	tempName = ReturnList(FilteredData['TimeString'])
	time = [str(i) for i in FilteredData.TimeString]
	l, = plt.plot(time, FilteredData.VarValue)
	d = plt.scatter(time, FilteredData.VarValue)
	plt.grid(True)
	axcolor = 'lightgoldenrodyellow'
	axpos = plt.axes([0.1, 0.1, 0.8, 0.03])
	maxx,minx = MinMax(tempName)
	spos = Slider(ax=axpos,
		label='Slider 2',
		valmin=0,
		valmax=maxx-5,
		valfmt='%1.2f',
		valstep=1,
		closedmax=True,
		color='green')
	def update(val):
		pos = spos.val
		ymin, ymax = ax.get_ylim()
		ax.axis([pos,pos+5,ymin, ymax])
		fig.canvas.draw_idle()
	update(minx)
	spos.on_changed(update)
	plt.show()

# ******************************************** Menu ********************************************************
menu=tk.Menu(root)
root.config(menu=menu)
file = tk.Menu(menu)
file.add_command(label='OpenFile',command=lambda:selectFolder())

menu.add_cascade(label="File",menu=file)
PlotData = tk.Menu(menu)
PlotData.add_command(label='Line Plot',command=lambda:LinePlot())
menu.add_cascade(label='Plots',menu=PlotData)

ExportMENU = tk.Menu(menu)
ExportMENU.add_command(label='Export PDF',command=lambda:ExportPDF())
ExportMENU.add_command(label='Export CSV',command=lambda:ExportCSV())
menu.add_cascade(label = 'Export',menu=ExportMENU)

menu.add_cascade(label = 'Clear',command=ClearFilter)

# ********************************************** Left SideBar ***********************************************
LeftSideBar=tk.Frame(root,borderwidth=3,relief="flat",width=200,height=500,bg='#cfcfcf')
LeftSideBar.pack(side='left',fill='y')
fileTitle = tk.Label(LeftSideBar,text="Select File",width=10)
fileTitle.pack(side='top',fill='x')
# === Left Files === #
leftFile=tk.Frame(LeftSideBar,borderwidth=3,relief="flat",width=200,height=300)
leftFile.pack(side='top',fill="x")
ListScroll=tk.Scrollbar(leftFile)
ListScroll.pack(side='right',fill="y")
listBox = tk.Listbox(leftFile,font=("Verdana",16),height=5,name="listBox")
listBox.bind('<ButtonRelease-1>',GetSelectedFile)
listBox.pack(side='top',fill='y',expand = True)
ListScroll.config(command=listBox.yview)
listBox.config(yscrollcommand=ListScroll.set)

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === Date Filter === #
DateFrame = tk.Frame(LeftSideBar)
DateFrame.pack(side="top",fill="x")
ttk.Label(DateFrame, text='Choose date').pack()
cal = DateEntry(DateFrame, width=12, background='darkblue',selectmode='day', date_pattern='dd/mm/y', foreground='white', borderwidth=2)
cal.pack(side='left',ipady=1,ipadx=15,padx=5,pady=5,anchor='n')
ttk.Button(DateFrame, text="ok", command=DateFilter).pack(side='right',ipady=1,ipadx=15,padx=5,pady=5,anchor='n')

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === Max Date Filter === #
DateFrame = tk.Frame(LeftSideBar)
DateFrame.pack(side="top",fill="x")
tk.Label(DateFrame,text='Range Filter').grid(row=0,column=1,sticky='n')
tk.Label(DateFrame,text='From Date').grid(row=1,column=0,sticky='e')
cal1 = DateEntry(DateFrame, width=12, background='darkblue',selectmode='day', date_pattern='dd/mm/y', foreground='white', borderwidth=2)
cal1.grid(row=1,column=3)
tk.Label(DateFrame,text='To Date').grid(row=2,column=0,sticky='e')
cal2 = DateEntry(DateFrame, width=12, background='darkblue',selectmode='day', date_pattern='dd/mm/y', foreground='white', borderwidth=2)
cal2.grid(row=2,column=3)
ttk.Button(DateFrame, text="ok", command=BetweenDate).grid(row=3,column=0,columnspan=4,sticky='n',pady=3)

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === Order Filter === #
OrderFrame=tk.Frame(LeftSideBar)
OrderFrame.pack(side="top",fill="x")
OrderTitle=tk.Label(OrderFrame,text="Order Filter")
OrderTitle.pack(side="top",fill="x")
select.set('None')
ColumnList = tk.OptionMenu(OrderFrame,select, *choices)
ColumnList.pack(side="left")
tk.Radiobutton(OrderFrame,text='ASC',variable=select.get(),value=True,width=4).pack(side='left',ipady=5,ipadx=20,anchor = 'n')
tk.Radiobutton(OrderFrame,text='DES',variable=select.get(),value=False,width=4).pack(side='left',ipady=5,ipadx=20,anchor='n')

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === MIN Slider FIlter === #
SliderFrame = tk.Frame(LeftSideBar)
SliderFrame.pack(side="top",fill="x")
SliderTitle=tk.Label(SliderFrame,text="MIN Slider Filter")
SliderTitle.pack(side="top",fill="x")
SliderBar = tk.Scale(SliderFrame, from_=0, to=50,resolution=0.1, orient="horizontal",length=150,command=MinFilter)
SliderBar.pack(side="top",fill='x',padx=15,pady=3)

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === MAX Slider FIlter === #
SliderFrame = tk.Frame(LeftSideBar)
SliderFrame.pack(side="top",fill="x")
SliderTitle=tk.Label(SliderFrame,text="MAX Slider Filter")
SliderTitle.pack(side="top",fill="x")
SliderBar = tk.Scale(SliderFrame, from_=0, to=200, orient="horizontal",resolution=0.1,length=150,command=MaxFilter)
SliderBar.pack(side="top",fill='x',padx=15,pady=3)

Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# === Entry Slider FIlter === #
IndexFrame = tk.Frame(LeftSideBar)
IndexFrame.pack(side="top",fill="x")
IndexTitle=tk.Label(IndexFrame,text="Entry Filter")
IndexTitle.pack(side="top",fill="x")
option.set('Head')
IndexTitle=tk.OptionMenu(IndexFrame,option,'Head','Tail')
IndexTitle.pack(side="left",anchor='w')
Entry = tk.Entry(IndexFrame,width=30,textvariable=count)
Entry.pack(side="right",padx=15,pady=10)
Entry.bind('<Return>', SetBoundry)


Temp = tk.Label(LeftSideBar,text="",bg='#cfcfcf',borderwidth=0,relief='flat')
Temp.pack(side='top',fill='x')

# ***************************************** Middle SideBar *****************************************************
MiddleSideBar=tk.Frame(root,borderwidth=3,relief="flat",bg='#a3cfcf')
MiddleSideBar.pack(side='top',fill='both')
dataScroll=tk.Scrollbar(MiddleSideBar)
dataScroll.pack(side='left',fill="y")
MiddleTreeView=tk.Frame(MiddleSideBar,width=500,height=500)
MiddleTreeView.pack(side='left')
DataView = ttk.Treeview(MiddleTreeView,columns=('h1','h2','h3','h4','h5'),height=32)
dataScroll.config(command=DataView.yview)
DataView.config(yscrollcommand=dataScroll.set)
DataView.pack(side='top',fill='both')
bottomScroll=tk.Scrollbar(MiddleTreeView,orient='horizontal')
bottomScroll.pack(side='bottom',fill='x')
bottomScroll.config(command=DataView.xview)
DataView.config(xscrollcommand=bottomScroll.set)

# ******************************************* left config  *****************************************************
if not(os.path.exists("log.txt")):
	selectFolder()
else:
	f = open('log.txt','r')
	dire=f.readline()
	f.close()
	if not(os.path.exists(dire)):
		selectFolder()
	else:
		ShowCSV()
root.mainloop()