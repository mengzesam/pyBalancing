import sys
import numpy
from PyQt5.QtCore import Qt,QCoreApplication
from PyQt5.QtWidgets import (
    QApplication,QWidget,QDialog,QTextBrowser,QVBoxLayout
    )
from PyQt5.QtGui import QColor 
from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from Ui_Balance import Ui_BalanceForm

class PyBalance(QWidget):  
    PLOT_WIDTH=11
    PLOT_R=3.5  
    PLOT_R2=1.5*PLOT_R
    PLOT_R3=1.3*PLOT_R
    PLOT_WISE_ARCANGLE=30
    PLOT_ARROW_ANGLE=30
    PLOT_ARROW_LENGTH=0.1*PLOT_R
    PLOT_DOTNUM=161
    PLOT_COLORS=['red','blue','black','green','cyan','magenta','red','plum','brown','purple','darkblue','crimson']
    PLOT_LW=1
    def __init__(self,parent=None):
        super(PyBalance,self).__init__(parent)
        self.ui=Ui_BalanceForm()
        self.ui.setupUi(self)
        self.ui.retranslateUi(self)
        #self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        #self.setFixedSize(-10+QApplication.desktop().availableGeometry().width()
        #            ,-30+QApplication.desktop().availableGeometry().height())
        self.setFixedHeight(480)
        self.setWindowTitle('vibration balance')
        self.fig=None
        self.ax=None
        self.line_Qx=None
        self.line_Qy=None
        self.line_wise=None
        self.line_Ax=None
        self.line_Px=None
        self.line_Ay=None
        self.line_Py=None
        self.line_key=None
        self.line_keypos=None
        self.line_Xpos=None
        self.line_Ypos=None
        self.annotate_wise=None
        self.annotate_key=None
        self.annotate_Xpos=None
        self.annotate_Ypos=None
        self.annotate_Ax=None
        self.annotate_Px=None
        self.annotate_Ay=None
        self.annotate_Py=None
        self.clockwise=-1
        self.keypos=0
        self.Xpos=45
        self.Ypos=135
        self.Xamp=100
        self.Xpha=65
        self.Xlag=25
        self.Yamp=100
        self.Ypha=345
        self.Ylag=25
        self.shaftmass=10000
        self.RPM=3000
        self.radius=400
        self.weight=500
        self.unit_kgf=4.028410
        self.all_kgf=2014.204980
        self.excited_percent=20.142050
        self.initPlot()
        self.setupConnect()

    def setupConnect(self):
        self.ui.CMBoxClockwise.currentIndexChanged.connect(lambda index:self.onPlotCtrlChanged(0,index))
        self.ui.DSBoxKeyPos.editingFinished.connect(lambda:self.onPlotCtrlChanged(1,self.ui.DSBoxKeyPos.value()))
        self.ui.DSBoxXPos.editingFinished.connect(lambda:self.onPlotCtrlChanged(2,self.ui.DSBoxXPos.value()))
        self.ui.DSBoxYPos.editingFinished.connect(lambda:self.onPlotCtrlChanged(3,self.ui.DSBoxYPos.value()))
        self.ui.DSBoxXamp.editingFinished.connect(lambda:self.onPlotCtrlChanged(4,self.ui.DSBoxXamp.value()))
        self.ui.DSBoxXpha.editingFinished.connect(lambda:self.onPlotCtrlChanged(5,self.ui.DSBoxXpha.value()))
        self.ui.DSBoxXlag.editingFinished.connect(lambda:self.onPlotCtrlChanged(6,self.ui.DSBoxXlag.value()))
        self.ui.DSBoxYamp.editingFinished.connect(lambda:self.onPlotCtrlChanged(7,self.ui.DSBoxYamp.value()))
        self.ui.DSBoxYpha.editingFinished.connect(lambda:self.onPlotCtrlChanged(8,self.ui.DSBoxYpha.value()))
        self.ui.DSBoxYlag.editingFinished.connect(lambda:self.onPlotCtrlChanged(9,self.ui.DSBoxYlag.value()))
        self.ui.DSBoxMass.editingFinished.connect(lambda:self.onPlotCtrlChanged(10,self.ui.DSBoxMass.value()))
        self.ui.DSBoxRPM.editingFinished.connect(lambda:self.onPlotCtrlChanged(11,self.ui.DSBoxRPM.value()))
        self.ui.DSBoxRadius.editingFinished.connect(lambda:self.onPlotCtrlChanged(12,self.ui.DSBoxRadius.value()))
        self.ui.DSBoxWeight.editingFinished.connect(lambda:self.onPlotCtrlChanged(13,self.ui.DSBoxWeight.value()))
        self.ui.CheckDispAx.stateChanged.connect(lambda state:(
            self.line_Ax.set_visible(bool(state)),
            self.ui.CheckDispAxLabel.setChecked(bool(state))
        ))
        self.ui.CheckDispAxLabel.stateChanged.connect(lambda state:(
            self.annotate_Ax.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispPx.stateChanged.connect(lambda state:(
            self.line_Px.set_visible(bool(state)),
            self.ui.CheckDispPxLabel.setChecked(bool(state))
        ))
        self.ui.CheckDispPxLabel.stateChanged.connect(lambda state:(
            self.annotate_Px.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispAy.stateChanged.connect(lambda state:(
            self.line_Ay.set_visible(bool(state)),
            self.ui.CheckDispAyLabel.setChecked(bool(state))
        ))
        self.ui.CheckDispAyLabel.stateChanged.connect(lambda state:(
            self.annotate_Ay.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispPy.stateChanged.connect(lambda state:(
            self.line_Py.set_visible(bool(state)),
            self.ui.CheckDispPyLabel.setChecked(bool(state))
        ))
        self.ui.CheckDispPyLabel.stateChanged.connect(lambda state:(
            self.annotate_Py.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispQx.stateChanged.connect(lambda state:(
            self.line_Qx.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispQy.stateChanged.connect(lambda state:(
            self.line_Qy.set_visible(bool(state)),
            self.fig.canvas.draw()
        ))
        self.ui.CheckDispAll.stateChanged.connect(lambda state:(
            self.ui.CheckDispAx.setChecked(bool(state)),
            self.ui.CheckDispPx.setChecked(bool(state)),
            self.ui.CheckDispAy.setChecked(bool(state)),
            self.ui.CheckDispPy.setChecked(bool(state)),
            self.ui.CheckDispQx.setChecked(bool(state)),
            self.ui.CheckDispQy.setChecked(bool(state))
        )) 
        self.ui.BTNHelp.clicked.connect(self.onPlotHelp)

    def onPlotHelp(self):
        helpDlg=QDialog(self)
        helpDlg.resize(300,240)
        helpDlg.setWindowTitle('Help')
        vLayout0=QVBoxLayout(helpDlg)
        vLayout=QVBoxLayout()
        text=QTextBrowser(helpDlg)
        vLayout.addWidget(text)  
        vLayout0.addLayout(vLayout)
        text.setText('\
            <H4><font color=blue>Φ为键相探头位置</font>\
            <H4><font color=blue>Qx,Qy:基于X测点和Y测点的加重位置,其角度为键相点\
                <font color=red>逆转向</font>到加重点夹角</font>\
            <H4><font color=blue>Ax,Ay:基于X和Y测点的振动高点位置,其角度为键相点\
                <font color=red>逆转向</font>的夹角</font>\
            <H4><font color=blue>Px,Py:基于X和Y测点的激振力位置,从其出发\
                <font color=red>逆转向</font>到振动高点的夹角为机械滞后角</font>\
            <H3><font color=blue>编写于2020.5.24江西黄金埠出差宾馆</font>\
            <H3><font color=blue>QQ:383238372</font>\
            <H3><font color=blue>email:mengzesam@126.com</font>\
        ')      
        helpDlg.exec()

    def initPlot(self):
        self.ui.tabWidget.setTabText(0,'balancing plot')
        #设置参数
        if(self.clockwise==1):
            self.ui.CMBoxClockwise.setCurrentIndex(0)
        else:
            self.ui.CMBoxClockwise.setCurrentIndex(1)
        self.ui.DSBoxKeyPos.setValue(self.keypos)
        self.ui.DSBoxXPos.setValue(self.Xpos)
        self.ui.DSBoxYPos.setValue(self.Ypos)
        self.ui.DSBoxXamp.setValue(self.Xamp)
        self.ui.DSBoxXpha.setValue(self.Xpha)
        self.ui.DSBoxXlag.setValue(self.Xlag)
        self.ui.DSBoxYamp.setValue(self.Yamp)
        self.ui.DSBoxYpha.setValue(self.Ypha)
        self.ui.DSBoxYlag.setValue(self.Ylag)
        XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360
        self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos))
        YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
        self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos))
        self.ui.DSBoxMass.setValue(self.shaftmass)
        self.ui.DSBoxRPM.setValue(self.RPM)
        self.ui.DSBoxRadius.setValue(self.radius)
        self.ui.DSBoxWeight.setValue(self.weight)
        self.ui.TextUnitKgf.setText('{:.2f}'.format(self.unit_kgf))
        self.ui.TextAllKgf.setText('{:.2f}'.format(self.all_kgf))
        self.ui.TextPercent.setText('{:.2f}'.format(self.excited_percent))
        self.ui.TextXweightpos.setStyleSheet('background-color:rgba(0,255,0,255)')
        self.ui.TextYweightpos.setStyleSheet('background-color:rgba(0,255,0,255)')
        self.ui.TextUnitKgf.setStyleSheet('background-color:rgba(0,255,0,255)')
        self.ui.TextAllKgf.setStyleSheet('background-color:rgba(0,255,0,255)')        
        self.ui.TextPercent.setStyleSheet('background-color:rgba(0,255,0,255)')
        #结束设置        
        canvas = FigureCanvas(Figure(tight_layout=True))
        self.ui.LayoutTab1Plot.addWidget(canvas)
        self.fig=canvas.figure
        self.fig.set_size_inches(6.4,6.4)
        self.ax=self.fig.subplots()
        spines=['left','top','right','bottom']
        for el in spines:
            self.ax.spines[el].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.axis('equal') #[-self.PLOT_WIDTH/2,self.PLOT_WIDTH/2,-self.PLOT_WIDTH/2,self.PLOT_WIDTH/2])
        lw=self.PLOT_LW
        self.ax.plot([-self.PLOT_WIDTH/2,self.PLOT_WIDTH/2,self.PLOT_WIDTH/2,-self.PLOT_WIDTH/2,-self.PLOT_WIDTH/2],
                [self.PLOT_WIDTH/2,self.PLOT_WIDTH/2,-self.PLOT_WIDTH/2,-self.PLOT_WIDTH/2,self.PLOT_WIDTH/2],
                linewidth=lw,color='black',dashes=[1,2,5,2],visible=False)
        self.ax.scatter(0,0,s=9,c=self.PLOT_COLORS[0])
        t=numpy.linspace(0,2*numpy.pi,self.PLOT_DOTNUM)
        x=numpy.cos(t)*self.PLOT_R
        y=numpy.sin(t)*self.PLOT_R
        self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[1])         
        #画转向线       
        beta=self.PLOT_WISE_ARCANGLE
        ang1=numpy.pi/2-beta*numpy.pi/360.0
        ang2=numpy.pi/2+beta*numpy.pi/360.0
        t=numpy.linspace(ang1,ang2,self.PLOT_DOTNUM)
        x=numpy.cos(t)*self.PLOT_R2
        y=numpy.sin(t)*self.PLOT_R2
        self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[2])
        #转向箭头
        #if(self.clockwise==1):
        alpha=180.0-beta/2.0
        x0=x[0]
        y0=y[0]
        if(self.clockwise!=1):
            alpha=beta/2.0            
            x0=x[-1]
            y0=y[-1]
        beta=self.PLOT_ARROW_ANGLE
        ang1=(alpha-beta/2.0)*numpy.pi/180.0
        ang2=(alpha+beta/2.0)*numpy.pi/180.0
        length=self.PLOT_ARROW_LENGTH
        x=[x0,numpy.cos(ang1)*length+x0,numpy.cos(ang2)*length+x0,x0]
        y=[y0,numpy.sin(ang1)*length+y0,numpy.sin(ang2)*length+y0,y0]
        self.line_wise,=self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[2])
        Xoff=0
        if(self.clockwise!=1):
            Xoff=-5.0*self.PLOT_ARROW_LENGTH            
        self.annotate_wise=self.ax.annotate('{}RPM'.format(int(self.RPM)),(x0+Xoff,y0),
            color=self.PLOT_COLORS[2],fontsize='x-small')
        #X探头，Y探头，键相位置
        lines=[None,None,None]   
        annotates=[None,None,None]     
        texts=['X','Y','Φ']
        alphas=[self.Xpos,self.Ypos,self.keypos]
        cos1=1 
        sin1=0
        for i,alpha in enumerate(alphas):
            alpha=(alpha+360)%360
            ang1=alpha*numpy.pi/180.0
            cos1=numpy.cos(ang1) 
            sin1=numpy.sin(ang1)
            x0=cos1*self.PLOT_R3
            y0=sin1*self.PLOT_R3
            x=[x0+cos1*self.PLOT_ARROW_LENGTH,x0,x0-sin1*self.PLOT_ARROW_LENGTH,x0+sin1*self.PLOT_ARROW_LENGTH]
            y=[y0+sin1*self.PLOT_ARROW_LENGTH,y0,y0+cos1*self.PLOT_ARROW_LENGTH,y0-cos1*self.PLOT_ARROW_LENGTH]
            lines[i],=self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[3+i])
            Xoff=self.PLOT_ARROW_LENGTH
            if(alpha>120 and alpha<=300):
                Xoff=-0.9*self.PLOT_ARROW_LENGTH
                x0=x0+cos1*self.PLOT_ARROW_LENGTH
                y0=y0+sin1*self.PLOT_ARROW_LENGTH
                if(alpha>250):y0=y0-0.5*self.PLOT_ARROW_LENGTH
            annotates[i]=self.ax.annotate(texts[i],(x0+Xoff,y0),
                color=self.PLOT_COLORS[3+i],fontsize='small')
        self.line_Xpos,self.line_Ypos,self.line_keypos=lines
        self.annotate_Xpos,self.annotate_Ypos,self.annotate_key=annotates
        x=[0,cos1*self.PLOT_R]
        y=[0,sin1*self.PLOT_R]
        self.line_key,=self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[5],dashes=[2,1,2,1])
        #Ax,Px,Ay,Py
        lines=[None,None,None,None]
        annotates=[None,None,None,None]
        texts=['Ax','Px','Ay','Py']        
        alphas=[self.Xpos+self.clockwise*self.Xpha,self.Xpos+self.clockwise*(self.Xpha-self.Xlag),
                self.Ypos+self.clockwise*self.Ypha,self.Ypos+self.clockwise*(self.Ypha-self.Ylag)]
        for i,alpha in enumerate(alphas):
            alpha=(alpha+360)%360
            ang1=alpha*numpy.pi/180.0
            ang2=ang1+numpy.pi+self.PLOT_ARROW_ANGLE*numpy.pi/360.0
            ang3=ang1+numpy.pi-self.PLOT_ARROW_ANGLE*numpy.pi/360.0
            cos1=numpy.cos(ang1) 
            sin1=numpy.sin(ang1)
            x0=cos1*self.PLOT_R
            y0=sin1*self.PLOT_R
            x=[0,x0,x0+numpy.cos(ang2)*self.PLOT_ARROW_LENGTH,x0+numpy.cos(ang3)*self.PLOT_ARROW_LENGTH,x0]
            y=[0,y0,y0+numpy.sin(ang2)*self.PLOT_ARROW_LENGTH,y0+numpy.sin(ang3)*self.PLOT_ARROW_LENGTH,y0]
            lines[i],=self.ax.plot(x,y,linewidth=lw,color=self.PLOT_COLORS[6+i])            
            Xoff=0.2*self.PLOT_ARROW_LENGTH
            if(alpha>90 and alpha<=270):
                Xoff=-1.2*self.PLOT_ARROW_LENGTH
            if(i>=2):#for Ay,Py
                x0=cos1*(0.7*self.PLOT_R)
                y0=sin1*(0.7*self.PLOT_R)
                Xoff=-1.5*self.PLOT_ARROW_LENGTH
            annotates[i]=self.ax.annotate(texts[i],(x0+Xoff,y0),
                color=self.PLOT_COLORS[6+i],fontsize='small')
        self.line_Ax,self.line_Px,self.line_Ay,self.line_Py=lines
        self.annotate_Ax,self.annotate_Px,self.annotate_Ay,self.annotate_Py=annotates
        #scatter Qx,Qy,which are the weighting positions
        alpha=XWeightpos*self.clockwise+self.keypos
        ang1=numpy.pi*alpha/180.0
        self.line_Qx,=self.ax.plot([numpy.cos(ang1)*self.PLOT_R],[numpy.sin(ang1)*self.PLOT_R],
            marker='o',markersize=4,markerfacecolor=self.PLOT_COLORS[-1],color=self.PLOT_COLORS[-1],
            linewidth=lw,label='Qx∠{:.0f}°'.format(XWeightpos))
        alpha=YWeightpos*self.clockwise+self.keypos
        ang1=numpy.pi*alpha/180.0
        self.line_Qy,=self.ax.plot([numpy.cos(ang1)*self.PLOT_R],[numpy.sin(ang1)*self.PLOT_R],
            marker='D',markersize=4,markerfacecolor=self.PLOT_COLORS[-2],color=self.PLOT_COLORS[-2],
            linewidth=lw,label='Qy∠{:.0f}°'.format(YWeightpos))
        self.ax.legend()
    
    def onPlotCtrlChanged(self,ctrlIndex,value):
        err=1e-6
        if(ctrlIndex==0):
            self.clockwise=-2*value+1
            self.updatePlotLineWise()
            alpha=self.Xpos+self.clockwise*self.Xpha
            self.updatePlotAxyPxy(alpha,self.line_Ax,self.annotate_Ax,self.PLOT_COLORS[6])
            alpha=self.Xpos+self.clockwise*(self.Xpha-self.Xlag)
            self.updatePlotAxyPxy(alpha,self.line_Px,self.annotate_Px,self.PLOT_COLORS[7])
            alpha=self.Ypos+self.clockwise*self.Ypha
            self.updatePlotAxyPxy(alpha,self.line_Ay,self.annotate_Ay,self.PLOT_COLORS[8])
            alpha=self.Ypos+self.clockwise*(self.Ypha-self.Ylag)
            self.updatePlotAxyPxy(alpha,self.line_Py,self.annotate_Py,self.PLOT_COLORS[9])
            self.updateQxQy()
            self.fig.canvas.draw()
            XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
            self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos))           
            YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
            self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos))
        elif(ctrlIndex==1 and abs(self.keypos-value)>err):
            self.keypos=value
            self.updatePlotXYKeyPos(self.keypos,self.line_keypos,self.annotate_key,self.PLOT_COLORS[5])
            self.updateQxQy()
            self.fig.canvas.draw()
            XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
            self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos))          
            YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
            self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos))   
        elif(ctrlIndex==2 and abs(self.Xpos-value)>err):
            self.Xpos=value
            self.updatePlotXYKeyPos(self.Xpos,self.line_Xpos,self.annotate_Xpos,self.PLOT_COLORS[3])
            alpha=self.Xpos+self.clockwise*self.Xpha
            self.updatePlotAxyPxy(alpha,self.line_Ax,self.annotate_Ax,self.PLOT_COLORS[6])
            alpha=self.Xpos+self.clockwise*(self.Xpha-self.Xlag)
            self.updatePlotAxyPxy(alpha,self.line_Px,self.annotate_Px,self.PLOT_COLORS[7])
            self.updateQxQy()
            self.fig.canvas.draw()
            XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
            self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos))   
        elif(ctrlIndex==3 and abs(self.Ypos-value)>err):
            self.Ypos=value
            self.updatePlotXYKeyPos(self.Ypos,self.line_Ypos,self.annotate_Ypos,self.PLOT_COLORS[4])
            alpha=self.Ypos+self.clockwise*self.Ypha
            self.updatePlotAxyPxy(alpha,self.line_Ay,self.annotate_Ay,self.PLOT_COLORS[8])
            alpha=self.Ypos+self.clockwise*(self.Ypha-self.Ylag)
            self.updatePlotAxyPxy(alpha,self.line_Py,self.annotate_Py,self.PLOT_COLORS[9])
            self.updateQxQy()
            self.fig.canvas.draw()         
            YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
            self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos)) 
        elif(ctrlIndex==4 and abs(self.Xamp-value)>err):
            self.Xamp=value
        elif(ctrlIndex==5 and abs(self.Xpha-value)>err):
            self.Xpha=value
            alpha=self.Xpos+self.clockwise*self.Xpha
            self.updatePlotAxyPxy(alpha,self.line_Ax,self.annotate_Ax,self.PLOT_COLORS[6])
            alpha=self.Xpos+self.clockwise*(self.Xpha-self.Xlag)
            self.updatePlotAxyPxy(alpha,self.line_Px,self.annotate_Px,self.PLOT_COLORS[7])
            self.updateQxQy()
            self.fig.canvas.draw()
            XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
            self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos))  
        elif(ctrlIndex==6 and abs(self.Xlag-value)>err):
            self.Xlag=value
            alpha=self.Xpos+self.clockwise*(self.Xpha-self.Xlag)
            self.updatePlotAxyPxy(alpha,self.line_Px,self.annotate_Px,self.PLOT_COLORS[7])
            self.updateQxQy()
            self.fig.canvas.draw()
            XWeightpos=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
            self.ui.TextXweightpos.setText('{:.2f}'.format(XWeightpos)) 
        elif(ctrlIndex==7 and abs(self.Yamp-value)>err):
            self.Yamp=value
        elif(ctrlIndex==8 and abs(self.Ypha-value)>err):
            self.Ypha=value
            alpha=self.Ypos+self.clockwise*self.Ypha
            self.updatePlotAxyPxy(alpha,self.line_Ay,self.annotate_Ay,self.PLOT_COLORS[8])
            alpha=self.Ypos+self.clockwise*(self.Ypha-self.Ylag)
            self.updatePlotAxyPxy(alpha,self.line_Py,self.annotate_Py,self.PLOT_COLORS[9])
            self.updateQxQy()
            self.fig.canvas.draw()         
            YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
            self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos)) 
        elif(ctrlIndex==9 and abs(self.Ylag-value)>err):
            self.Ylag=value
            alpha=self.Ypos+self.clockwise*(self.Ypha-self.Ylag)
            self.updatePlotAxyPxy(alpha,self.line_Py,self.annotate_Py,self.PLOT_COLORS[9])
            self.updateQxQy()
            self.fig.canvas.draw()        
            YWeightpos=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
            self.ui.TextYweightpos.setText('{:.2f}'.format(YWeightpos)) 
        elif(ctrlIndex==10 and abs(self.shaftmass-value)>err):
            self.shaftmass=value
            self.excited_percent=100.0*self.all_kgf/self.shaftmass
            self.ui.TextPercent.setText('{:.2f}'.format(self.excited_percent))
        elif(ctrlIndex==11 and abs(self.RPM-value)>err):
            self.RPM=value
            self.updatePlotLineWise()
            self.fig.canvas.draw()    
            self.unit_kgf=0.001*self.radius*(self.RPM/60*2*numpy.pi)**2/1000/9.8
            self.all_kgf=self.unit_kgf*self.weight
            self.excited_percent=100.0*self.all_kgf/self.shaftmass
            self.ui.TextUnitKgf.setText('{:.2f}'.format(self.unit_kgf))
            self.ui.TextAllKgf.setText('{:.2f}'.format(self.all_kgf))
            self.ui.TextPercent.setText('{:.2f}'.format(self.excited_percent))
        elif(ctrlIndex==12 and abs(self.radius-value)>err):
            self.radius=value
            self.unit_kgf=0.001*self.radius*(self.RPM/60*2*numpy.pi)**2/1000/9.8
            self.all_kgf=self.unit_kgf*self.weight
            self.excited_percent=100.0*self.all_kgf/self.shaftmass
            self.ui.TextUnitKgf.setText('{:.2f}'.format(self.unit_kgf))
            self.ui.TextAllKgf.setText('{:.2f}'.format(self.all_kgf))
            self.ui.TextPercent.setText('{:.2f}'.format(self.excited_percent))
        elif(ctrlIndex==13 and abs(self.weight-value)>err):
            self.weight=value
            self.all_kgf=self.unit_kgf*self.weight
            self.excited_percent=100.0*self.all_kgf/self.shaftmass
            self.ui.TextAllKgf.setText('{:.2f}'.format(self.all_kgf))
            self.ui.TextPercent.setText('{:.2f}'.format(self.excited_percent))

    def updatePlotLineWise(self):
        if(self.line_wise is None):return
        beta=self.PLOT_WISE_ARCANGLE    
        ang1=numpy.pi/2-beta*numpy.pi/360.0
        alpha=180.0-beta/2.0       
        if(self.clockwise==-1):         
            ang1=numpy.pi/2+beta*numpy.pi/360.0
            alpha=beta/2.0                   
        x0=numpy.cos(ang1)*self.PLOT_R2
        y0=numpy.sin(ang1)*self.PLOT_R2
        beta=self.PLOT_ARROW_ANGLE
        ang1=(alpha-beta/2.0)*numpy.pi/180.0
        ang2=(alpha+beta/2.0)*numpy.pi/180.0
        length=self.PLOT_ARROW_LENGTH
        x=[x0,numpy.cos(ang1)*length+x0,numpy.cos(ang2)*length+x0,x0]
        y=[y0,numpy.sin(ang1)*length+y0,numpy.sin(ang2)*length+y0,y0]
        self.line_wise.set_data(x,y)        
        Xoff=0
        if(self.clockwise!=1):
            Xoff=-5.0*self.PLOT_ARROW_LENGTH 
        self.annotate_wise.set_position((x0+Xoff,y0))           
        self.annotate_wise.set_text('{}RPM'.format(int(self.RPM)))

    def updatePlotXYKeyPos(self,pos_alpha,line,annotate,color):
        if(line is None): return
        alpha=(pos_alpha+360)%360
        ang1=alpha*numpy.pi/180.0
        cos1=numpy.cos(ang1) 
        sin1=numpy.sin(ang1)
        x0=cos1*self.PLOT_R3
        y0=sin1*self.PLOT_R3
        x=[x0+cos1*self.PLOT_ARROW_LENGTH,x0,x0-sin1*self.PLOT_ARROW_LENGTH,x0+sin1*self.PLOT_ARROW_LENGTH]
        y=[y0+sin1*self.PLOT_ARROW_LENGTH,y0,y0+cos1*self.PLOT_ARROW_LENGTH,y0-cos1*self.PLOT_ARROW_LENGTH]
        line.set_data(x,y) 
        if(line==self.line_keypos and not self.line_key is None):      
            x=[0,cos1*self.PLOT_R]       
            y=[0,sin1*self.PLOT_R]
            self.line_key.set_data(x,y)
        Xoff=self.PLOT_ARROW_LENGTH
        if(alpha>120 and alpha<=300):
            Xoff=-0.9*self.PLOT_ARROW_LENGTH
            x0=x0+cos1*self.PLOT_ARROW_LENGTH
            y0=y0+sin1*self.PLOT_ARROW_LENGTH
            if(alpha>250):y0=y0-0.5*self.PLOT_ARROW_LENGTH
        annotate.set_position((x0+Xoff,y0))        

    def updatePlotAxyPxy(self,pos_alpha,line,annotate,color):
        if(line is None):return
        alpha=(pos_alpha+360)%360
        ang1=alpha*numpy.pi/180.0
        ang2=ang1+numpy.pi+self.PLOT_ARROW_ANGLE*numpy.pi/360.0
        ang3=ang1+numpy.pi-self.PLOT_ARROW_ANGLE*numpy.pi/360.0
        cos1=numpy.cos(ang1) 
        sin1=numpy.sin(ang1)
        x0=cos1*self.PLOT_R
        y0=sin1*self.PLOT_R
        x=[0,x0,x0+numpy.cos(ang2)*self.PLOT_ARROW_LENGTH,x0+numpy.cos(ang3)*self.PLOT_ARROW_LENGTH,x0]
        y=[0,y0,y0+numpy.sin(ang2)*self.PLOT_ARROW_LENGTH,y0+numpy.sin(ang3)*self.PLOT_ARROW_LENGTH,y0]
        line.set_data(x,y)       
        Xoff=0.2*self.PLOT_ARROW_LENGTH
        if(alpha>90 and alpha<=270):
            Xoff=-1.2*self.PLOT_ARROW_LENGTH
        if(annotate==self.annotate_Ay or annotate==self.annotate_Py):#for Ay,Py
            x0=cos1*(0.7*self.PLOT_R)
            y0=sin1*(0.7*self.PLOT_R)
            Xoff=-1.5*self.PLOT_ARROW_LENGTH
        annotate.set_position((x0+Xoff,y0))

    def updateQxQy(self):
        qx=(1260+self.clockwise*(self.Xpos+self.clockwise*(self.Xpha-self.Xlag)-self.keypos))%360 
        qy=(1260+self.clockwise*(self.Ypos+self.clockwise*(self.Ypha-self.Ylag)-self.keypos))%360
        weightposes=[qx,qy]
        labels=['Qx∠{:.0f}°'.format(qx),'Qy∠{:.0f}°'.format(qy)]
        QxQy=[self.line_Qx,self.line_Qy]  
        for i,pos in enumerate(weightposes):
            alpha=pos*self.clockwise+self.keypos  
            ang1=numpy.pi*alpha/180.0
            QxQy[i].set_data([numpy.cos(ang1)*self.PLOT_R],
                [numpy.sin(ang1)*self.PLOT_R])
            QxQy[i].set_label(labels[i])
        self.ax.legend()
        

if __name__ == "__main__":    
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling) #>=Qt5.6:Enables high-DPI scaling in Qt on supported platforms (see also High DPI Displays
    #QApplication.setStyle("fusion")
    app=QApplication(sys.argv)
    w=PyBalance()
    w.show()
    sys.exit(app.exec_())
    
