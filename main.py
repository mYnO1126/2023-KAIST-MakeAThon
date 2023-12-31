#import RPi.GPIO as GPIO
import time
import signal                   
import sys
import pygame
import serial
import numpy as np
import random
# import SmartFarmControl

TEMP_LIMIT=3.0
HUMID_LIMIT=20.0
SOIL_LIMIT=20.0
INFO_ICON_SIZE=(150,90)
NOTIFICATION_SIZE=(370,370)
POT_GRID=(3,4)


class Color():
    black=(0,0,0)
    gray=(224,224,224)
    white=(255,255,255)
    yellow=(255,184,0)
    magenta=(255,0,138)
    cyan=(82,0,255)
    skyblue=(0,240,255)
    green=(173,255,0)

class Info():
    def __init__(self,infos):
        self.critical=infos[0]
        self.temp=infos[1]
        self.status=infos[2]
        self.num=infos[3]
    def printInfo(self):
        return str(self.critical)+" "+str(self.temp)
    def getTemp(self):
        return self.temp
    def getStatus(self):
        return self.status
    def getCritical(self):
        return self.critical
    def getDone(self):
        if self.status=="Done":
            return True
        else:return False
    def getNum(self):
        return self.num


class Notice():
    def __init__(self,noticeNum, badPots, completePots):
        self.noticeNum=noticeNum
        self.badPots=badPots
        self.completePots=completePots
    def getNoticeNum(self):
        return self.noticeNum
    def getBatPots(self):
        return self.badPots
    def getCompletePots(self):
        return self.completePots


class potInfo():
    def __init__(self,potBool,infos):
        self.potBool=potBool
        self.infos=infos
    def updatePotInfo(self,potBool,infos):
        self.potBool=potBool
        self.infos=infos
    def getPotInfo(self):
        if self.infos is None:
            return None
        return self.infos
    def returnPotInfo(self):
        return self.potBool,self.getPotInfo()
    def dupInfo(self):
        if self.infos is None:
            return None
        return Info([self.infos.getCritical(),self.infos.getTemp(),self.infos.getStatus(),self.infos.getNum()])

class potGridInfo():
    def __init__(self,grid=POT_GRID):
        self.grid=grid
        nums=[2,5,7,10,11]
        self.PotInfos=[potInfo(False,None) for i in range(grid[0]*grid[1])]
        for i in range(len(nums)):
            self.PotInfos[nums[i]].updatePotInfo(True,Info((False,20+random.randint(0,10),"Good",i)))
        self.PotInfos[2].updatePotInfo(True,Info((False,25,"Done",0)))
        self.PotInfos[7].updatePotInfo(True,Info((True,25,"Bad",2)))



    def returnPotGridInfo(self,pos):
        return self.PotInfos[pos[0]*self.grid[1]+pos[1]].returnPotInfo()
    def printPotGridInfo(self):
        return "aaaa"
    def updatePotGridInfo(self,orig,dest):
        potBool,info=self.PotInfos[orig[0]*self.grid[1]+orig[1]].returnPotInfo()
        self.PotInfos[dest[0]*self.grid[1]+dest[1]]=potInfo(potBool,self.PotInfos[orig[0]*self.grid[1]+orig[1]].dupInfo())
        self.PotInfos[orig[0]*self.grid[1]+orig[1]].updatePotInfo(False,None)
    


class Button:
    def __init__(self,img_in,pos, img_act, action = None):
        self.width=img_in.get_width()
        self.height=img_in.get_height()
        self.img_in=img_in
        self.img_act=img_act
        self.pos=pos
        self.action=action
    def printScreen(self,display):
        display.blit(self.img_in,(self.pos[0]-self.width/2,self.pos[1]-self.height/2))
    def updateMouseOn(self,display,mouse):
        if self.pos[0] + self.width/2.0 > mouse[0] > self.pos[0]-self.width/2.0 and self.pos[1] + self.height/2.0 > mouse[1] > self.pos[1]-self.height/2.0:
            display.blit(self.img_act,(self.pos[0]-self.img_act.get_width()/2,self.pos[1]-self.img_act.get_height()/2))
        else:
            display.blit(self.img_in,(self.pos[0]-self.width/2,self.pos[1]-self.height/2))
    def updateClick(self,display,mouse):
        if self.pos[0] + self.width/2.0 > mouse[0] > self.pos[0]-self.width/2.0 and self.pos[1] + self.height/2.0 > mouse[1] > self.pos[1]-self.height/2.0:
            display.blit(self.img_act,(self.pos[0]-self.img_act.get_width()/2,self.pos[1]-self.img_act.get_height()/2))
            if self.action is not None:
                time.sleep(0.2)
                self.action()
class infoIcon:
    def __init__(self,img_in,name,info,unit,pos,size,thickness,radius,range):
        color=Color()
        self.img=img_in
        self.name=name
        self.info=info
        self.unit=unit
        self.pos=pos
        self.size=size
        self.thickness=thickness
        self.radius=radius
        self.range=range
        self.color=color.green
    
    def updateInfo(self,info):
        self.info=info

    def calculateColor(self,upper_bound,normal,lower_bound):
        color=Color()
        if normal is None:
            if self.name=="humid":
                up=np.array(color.cyan)
                down=np.array(color.gray)
            if self.name=="soil":
                up=np.array(color.skyblue)
                down=np.array(color.yellow)
            slope=(up-down)/(upper_bound-lower_bound)
            return down+slope*(self.info-lower_bound)
        else:
            if self.name=="temp":
                up=np.array(color.magenta)
                down=np.array(color.cyan)
                middle=np.array(color.green)
                if self.info>normal:
                    slope=(up-middle)/(upper_bound-normal)
                    return middle+slope*(upper_bound-self.info)
                else:
                    slope=(middle-down)/(normal-lower_bound)
                    return down+slope*(self.info-lower_bound)

    def setColor(self):
        color=Color()
        if self.name=="temp":
            self.color=self.calculateColor(50,25,0)
        if self.name=="humid":
            self.color=self.color=self.calculateColor(100,None,0)
        if self.name=="vent":
            if self.info==True:
                self.color=color.cyan
            else:
                self.color=color.magenta
        if self.name=="soil":
            self.color=self.calculateColor(100,None,0)
        
    def printScreen(self,display,info,font):
        self.updateInfo(info)
        self.setColor()
        pygame.draw.rect(
            display,
            self.color,
            pygame.Rect(
                (self.pos[0]-self.size[0]/2,self.pos[1]-self.size[1]/2),
                self.size,
            ),
            self.thickness,
            self.radius
        )
        display.blit(self.img,(self.pos[0]-self.size[0]/2+15,self.pos[1]-self.size[1]/2+20))

        if type(self.info)==bool:
            if self.info==True:
                text=font.render("On"+self.unit,True,self.color)
                text_rect=text.get_rect()
                text_rect.center=(self.pos[0]+25,self.pos[1])
            else:
                text=font.render("Off"+self.unit,True,self.color)
                text_rect=text.get_rect()
                text_rect.center=(self.pos[0]+25,self.pos[1])
        else:
            if type(self.info) is not str:
                text=font.render(str(self.info)+self.unit,True,self.color)
            else:
                text=font.render(self.info+self.unit,True,self.color)
            text_rect=text.get_rect()
            text_rect.center=(self.pos[0]+25,self.pos[1])
        display.blit(text,text_rect)
    
class Notification:
    def __init__(self,infos,pos,size,thickness,radius,mode, action = None):
        self.info=infos
        self.pos=pos
        self.size=size
        self.thickness=thickness
        self.radius=radius
        self.mode=mode
        self.action=action
    def printScreen(self,display,font):
        color=Color()
        pygame.draw.rect(
            display,
            color.gray,
            pygame.Rect(
                (self.pos[0]-self.size[0]/2,self.pos[1]-self.size[1]/2),
                self.size,
            ),
            self.thickness,
            self.radius,
        )
        if self.mode=="main":
            num=self.info.getNoticeNum()
            badPots=self.info.getBatPots()
            completePots=self.info.getCompletePots()

            potNums=np.array([x*POT_GRID[1]+y for [x,y] in badPots])
            completeNums=np.array([x*POT_GRID[1]+y for [x,y] in completePots])

            text1=font.render("Notices: "+str(num),True,color.black)
            text1_rect=text1.get_rect()
            text1_rect.center=(self.pos[0],self.pos[1]-30)
            display.blit(text1,text1_rect)


            text2=font.render("Pots: "+str(potNums),True,color.black)
            text2_rect=text2.get_rect()
            text2_rect.center=self.pos
            display.blit(text2,text2_rect)

            text3=font.render("Complete: "+str(completeNums),True,color.black)
            text3_rect=text3.get_rect()
            text3_rect.center=(self.pos[0],self.pos[1]+30)
            display.blit(text3,text3_rect)

        else:
            if self.info is None:
                text=font.render("No Pot Selected",True,color.gray)
                text_rect=text.get_rect()
                text_rect.center=self.pos
                display.blit(text,text_rect)
            else:
                temp=self.info.getTemp()
                status=self.info.getStatus()
                
                status="Status : "+status
                text1=font.render(status,True,color.black)
                text1_rect=text1.get_rect()
                text1_rect.center=(self.pos[0],self.pos[1]-20)

                tempStr="Temperature (°C): "+str(temp)
                text2=font.render(tempStr,True,color.black)
                text2_rect=text2.get_rect()
                text2_rect.center=(self.pos[0],self.pos[1]+20)

                display.blit(text1,text1_rect)
                display.blit(text2,text2_rect)

    def updateInfo(self,info):
        if info is None:
            self.info=None
        else:
            self.info=Info([info.getCritical(),info.getTemp(),info.getStatus(),info.getNum()])
    def updateClick(self,display,mouse):
        if self.pos[0] + self.size[0]/2.0 > mouse[0] > self.pos[0]-self.size[0]/2.0 and self.pos[1] + self.size[1]/2.0 > mouse[1] > self.pos[1]-self.size[1]/2.0:
            if self.action is not None:
                    time.sleep(0.2)
                    self.action()
    def interaction(self,display,mouse):
        return


class potGrid:
    def __init__(self,pos,size,thickness,radius,potGridInfo,font, action = None):
        self.pos=pos
        self.action=action
        self.size=size
        self.thickness=thickness
        self.radius=radius
        self.potGridInfo=potGridInfo
        self.font=font

        self.potSize=65
        self.gap=20
        self.offset=(25,70)
        self.selection=False
        self.selectedPot=[-1,-1]
        self.selectedInfo=None
        # self.img=self.drawPotGrid()        
    def printScreen(self,display):
        self.img=self.drawPotGrid()
        display.blit(self.img,(self.pos[0]-self.size[0]/2,self.pos[1]-self.size[1]/2))

    def updateClick(self,display,mouse):
        grid=self.checkMouseGrid(mouse)
        if self.action=="disabled":
            if grid is None:
                self.selection=False
                return False,None,None,None
            else:
                potBool,info=self.potGridInfo.returnPotGridInfo(grid)
                if self.selection:
                    if potBool:
                        self.selectedPot[0]=grid[0]
                        self.selectedPot[1]=grid[1]       
                        self.selectedInfo=info    
                        return False,info,None,None
                    else:
                        self.selection=False
                        return False,None,None,None
                else:
                    if potBool:
                        self.selection=True
                        self.selectedPot[0]=grid[0]
                        self.selectedPot[1]=grid[1]       
                        self.selectedInfo=info              
                    else:
                        self.selection=False   
                    return False,info,None,None
                
        elif self.action=="selection":
            if grid is None:
                self.selection=False 
                return False,None,None,None
            else:
                potBool,info=self.potGridInfo.returnPotGridInfo(grid)
                if self.selection:
                    if potBool:
                        self.selection=False
                        return False,None,None,None
                    else:
                        self.selection=False
                        return True,self.selectedInfo,self.selectedPot,grid
                else:
                    if potBool:
                        self.selection=True
                        self.selectedPot[0]=grid[0]
                        self.selectedPot[1]=grid[1]       
                        self.selectedInfo=info
                    else:
                        self.selection=False         
                    return False,info,None,None
                        


    # def updatePotGridInfo(self,potGridInfo):
    #     self.potGridInfo=potGridInfo
    def drawPotGrid(self):
        color=Color()
        potGridIcon = pygame.Surface(NOTIFICATION_SIZE)
        potGridIcon.fill(color.white)
        if self.selection:
            if self.action=="disabled":
                pygame.draw.rect(
                    potGridIcon,
                    color.skyblue,
                    pygame.Rect(
                        (0,0),
                        NOTIFICATION_SIZE,
                    ),
                    self.thickness,
                    self.radius,
                )
                x,y=POT_GRID
                for i in range(x):
                    for j in range(y):
                        potBool,info=self.potGridInfo.returnPotGridInfo((i,j))
                        if potBool:
                            if info.getCritical():
                                col=color.magenta
                            elif info.getDone():
                                col=color.cyan
                            else:
                                col=color.green
                        else:
                            col=color.gray
                        if i==self.selectedPot[0] and j==self.selectedPot[1]:
                            col=color.yellow
                            text=self.font.render(str(info.getNum()),True,color.black)
                            text_rect=text.get_rect()
                            text_rect.center=(self.offset[0]+j*(self.potSize+self.gap)+self.potSize/2,self.offset[1]+i*(self.potSize+self.gap)+self.potSize/2)
                            potGridIcon.blit(text,(self.offset[0]+j*(self.potSize+self.gap)+self.potSize/2,self.offset[1]+i*(self.potSize+self.gap)+self.potSize/2))
                        pygame.draw.rect(
                            potGridIcon,
                            col,
                            pygame.Rect(
                                (self.offset[0]+j*(self.potSize+self.gap),self.offset[1]+i*(self.potSize+self.gap)),
                                (self.potSize,self.potSize),
                            ),
                        )
            elif self.action=="selection":
                pygame.draw.rect(
                    potGridIcon,
                    color.skyblue,
                    pygame.Rect(
                        (0,0),
                        NOTIFICATION_SIZE,
                    ),
                    self.thickness,
                    self.radius,
                )
                x,y=POT_GRID
                for i in range(x):
                    for j in range(y):
                        potBool,info=self.potGridInfo.returnPotGridInfo((i,j))
                        if potBool:
                            col=color.gray
                        else:
                            col=color.green
                        if i==self.selectedPot[0] and j==self.selectedPot[1]:
                            col=color.yellow
                            text=self.font.render(str(info.getNum()),True,color.black)
                            text_rect=text.get_rect()
                            text_rect.center=(self.offset[0]+j*(self.potSize+self.gap)+self.potSize/2,self.offset[1]+i*(self.potSize+self.gap)+self.potSize/2)
                            potGridIcon.blit(text,text_rect)
                        pygame.draw.rect(
                            potGridIcon,
                            col,
                            pygame.Rect(
                                (self.offset[0]+j*(self.potSize+self.gap),self.offset[1]+i*(self.potSize+self.gap)),
                                (self.potSize,self.potSize),
                            ),
                        )
        else:
            pygame.draw.rect(
                potGridIcon,
                color.skyblue,
                pygame.Rect(
                    (0,0),
                    NOTIFICATION_SIZE,
                ),
                self.thickness,
                self.radius,
            )
            x,y=POT_GRID
            for i in range(x):
                for j in range(y):
                    potBool,info=self.potGridInfo.returnPotGridInfo((i,j))
                    if potBool:
                        text=self.font.render(str(info.getNum()),True,color.black)
                        text_rect=text.get_rect()
                        text_rect.center=(self.offset[0]+j*(self.potSize+self.gap)+self.potSize/2,self.offset[1]+i*(self.potSize+self.gap)+self.potSize/2)
                        potGridIcon.blit(text,text_rect)
                        if info.getCritical():
                            col=color.magenta
                        elif info.getDone():
                            col=color.cyan
                        else:
                            col=color.green
                    else:
                        col=color.gray
                    pygame.draw.rect(
                        potGridIcon,
                        col,
                        pygame.Rect(
                            (self.offset[0]+j*(self.potSize+self.gap),self.offset[1]+i*(self.potSize+self.gap)),
                            (self.potSize,self.potSize),
                        ),
                    )

        return potGridIcon
    def checkMouseGrid(self,mouse):
        grid=[-1,-1]
        mousePos=(mouse[0]-(self.pos[0]-self.size[0]/2),mouse[1]-(self.pos[1]-self.size[1]/2))
        for i in range(POT_GRID[0]):
            if self.offset[1]+(self.potSize+self.gap)*i<mousePos[1]<self.offset[1]+(self.potSize+self.gap)*(i+1)-self.gap:
                grid[0]=i
        for i in range(POT_GRID[1]):
            if self.offset[0]+(self.potSize+self.gap)*i<mousePos[0]<self.offset[0]+(self.potSize+self.gap)*(i+1)-self.gap:
                grid[1]=i
        if grid[0]==-1 or grid[1]==-1:
            return None
        else:
            return grid

class Process:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font=pygame.font.Font('freesansbold.ttf',20)
        self.noticeFont=pygame.font.Font('freesansbold.ttf',30)

        # self.arduino = serial.Serial('/dev/ttyACM0', 115200)

        self.color=Color()
        resolution = (1024,600)
        self.fps=30
        self.fpsClock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(resolution)#pygame.FULLSCREEN

        self.status="main"

        closeIcon=pygame.transform.scale(pygame.image.load("images/close_icon.jpg"),(50,50))
        clickClose=pygame.transform.scale(pygame.image.load("images/close_icon.jpg"),(40,40))
        self.stopButton = Button(closeIcon,(980,40),clickClose,end)

        settingsIcon=pygame.transform.scale(pygame.image.load("images/settings.png"),(50,50))
        clickSettings=pygame.transform.scale(pygame.image.load("images/settings.png"),(40,40))
        self.settingsButton=Button(settingsIcon,(40,560),clickSettings,self.settingsScreen)

        # self.farmControl=SmartFarmControl.SmartFarmControl()
        # self.farmControl.initializing_origin()

        self.info=[25.0,50.0,0,0,0,False]
        self.potGridInfo=potGridInfo(POT_GRID)
        self.updateSensorsRealTime=True
        self.sensorButtonCounter=0

    def updateSensorsInfos(self):
        # self.arduino.flushInput()
        # line = self.arduino.readline()
        # line = line.decode('euc-kr') # cp949 euc-kr utf-8
        # line = line.split()
        # for i in range(5):
        #     self.info[i]=line[i]
        return
    def stopSensorUpdate(self):
        self.sensorButtonCounter+=1
        if self.sensorButtonCounter%2==1:
            self.updateSensorsRealTime=False
            if self.sensorButtonCounter%3==1:
                self.info=[0,100,0,100,0,True]
            if self.sensorButtonCounter%3==0:
                self.info=[50,0,0,0,0,False]
        else:
            self.updateSensorsRealTime=True

    def mainScreen(self):
        tempIcon=pygame.transform.scale(pygame.image.load("images/temp.jpg"),(50,50))
        humidityIcon=pygame.transform.scale(pygame.image.load("images/humidity.png"),(50,50))
        ventilationIcon=pygame.transform.scale(pygame.image.load("images/ventilation.jpg"),(50,50))
        soilHumidityIcon=pygame.transform.scale(pygame.image.load("images/soil-humid.png"),(50,50))
        plantIcon=pygame.transform.scale(pygame.image.load("images/plant.png"),(170,170))
       
        temp=infoIcon(tempIcon,"temp",25,"°C",(212-45,520),INFO_ICON_SIZE,10,5,TEMP_LIMIT)
        humidity=infoIcon(humidityIcon,"humid",50,"%",(412-15,520),INFO_ICON_SIZE,10,5,HUMID_LIMIT)
        ventilation=infoIcon(ventilationIcon,"vent",False,"",(612+15,520),INFO_ICON_SIZE,10,5,0)
        soilHumidity=infoIcon(soilHumidityIcon,"soil",50,"%",(812+45,520),INFO_ICON_SIZE,10,5,SOIL_LIMIT)

        potSelectionIcon = pygame.Surface(NOTIFICATION_SIZE)
        potSelectionIcon.fill(self.color.white)
        pygame.draw.rect(
            potSelectionIcon,
            self.color.yellow,
            pygame.Rect(
                (0,0),
                NOTIFICATION_SIZE,
            ),
            15,
            20,
        )

        tot_notice=Notice(1,[[1,3]],[[0,2]])
        potSelectionIcon.blit(plantIcon,(NOTIFICATION_SIZE[0]/2.0-85,NOTIFICATION_SIZE[1]/2.0-85))
        potSelectionButton=Button(potSelectionIcon,(1024-280,260),potSelectionIcon,self.potSelectionScreen)
        notification=Notification(tot_notice,(280,260),NOTIFICATION_SIZE,15,20,"main",self.notificationScreen)

        buttons=[self.stopButton,self.settingsButton,potSelectionButton]
        self.infos=[temp,humidity,ventilation,soilHumidity]

        # printInfos(infos,self.screen,info,self.font)
        # printObjects(buttons,self.screen)
        count=0
        while True:
            count+=1
            if count%100==0:
                if self.updateSensorsRealTime:
                    self.updateSensorsInfos()
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            notification.printScreen(self.screen,self.noticeFont)
            printInfos(self.infos,self.screen,self.info,self.font)
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
                    notification.updateClick(self.screen,mouse)
            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def notificationScreen(self):
        backIcon=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(50,50))
        clickBack=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(40,40))
        potinfo=potInfo(False,None)

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)
        notification=Notification(potinfo.getPotInfo(),(280,260),NOTIFICATION_SIZE,15,20,"notice",None)
        potgrid=potGrid((1024-280,260),NOTIFICATION_SIZE,15,20,self.potGridInfo,self.font,"disabled")
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[potgrid]
        
        count=0
        while True:
            count+=1
            if count%100==0:
                if self.updateSensorsRealTime:
                    self.updateSensorsInfos()
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            notification.printScreen(self.screen,self.noticeFont)
            printObjects(objects,self.screen)
            printInfos(self.infos,self.screen,self.info,self.font)
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
                    notification.interaction(self.screen,mouse)
                    _,info,_,_=potgrid.updateClick(self.screen,mouse)
                    notification.updateInfo(info)
            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def potSelectionScreen(self):
        backIcon=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(50,50))
        clickBack=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(40,40))

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)
        notification=Notification(None,(1024-280,260),NOTIFICATION_SIZE,15,20,"potSelect",None)
        potgrid=potGrid((280,260),NOTIFICATION_SIZE,15,20,self.potGridInfo,self.font,"selection")
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[potgrid]

        count=0
        while True:
            count+=1
            if count%100==0:
                # if self.farmControl.checkOrigin() is False:
                #     self.farmControl.moveMotorsToOrigin()
                if self.updateSensorsRealTime:
                    self.updateSensorsInfos()
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            notification.printScreen(self.screen,self.noticeFont)
            printInfos(self.infos,self.screen,self.info,self.font)
            printObjects(objects,self.screen)
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
                    move,info,orig,dest=potgrid.updateClick(self.screen,mouse)
                    notification.updateInfo(info)        
                    notification.printScreen(self.screen,self.noticeFont)          
                    if move:
                        time.sleep(0.001)
                        # self.farmControl.moveMotorsOrigDest(orig,dest)
                        self.potGridInfo.updatePotGridInfo(orig,dest)
                        notification.updateInfo(None) 
                        

            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def settingsScreen(self):
        backIcon=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(50,50))
        clickBack=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(40,40))

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)

        stopSensorUpdateIcon = pygame.Surface((200,100))
        stopSensorUpdateIcon.fill(self.color.white)
        pygame.draw.rect(
            stopSensorUpdateIcon,
            self.color.magenta,
            pygame.Rect(
                (0,0),
                (200,100),
            ),
            15,
            20,
        )
        text=self.font.render("Stop Sensor Update",True,self.color.magenta)
        text_rect=text.get_rect()
        text_rect.center=(100,50)
        stopSensorUpdateIcon.blit(text,text_rect)

        stopSensorUpdateActIcon = pygame.transform.scale(stopSensorUpdateIcon,(110,60))

        stopSensorUpdateButton=Button(stopSensorUpdateIcon,(300,300),stopSensorUpdateActIcon,self.stopSensorUpdate)
        buttons=[self.stopButton,self.settingsButton,backButton,stopSensorUpdateButton]

        while True:
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
            pygame.display.flip()
            self.fpsClock.tick(self.fps)

def printInfos(infos,display,newInfo,font):
    infos[0].printScreen(display,int(newInfo[0]),font) #temp
    infos[1].printScreen(display,int(newInfo[1]),font) #humidity
    infos[2].printScreen(display,newInfo[5],font) #ventilation
    infos[3].printScreen(display,int(newInfo[3]),font) #soil
    # for i in range(len(infos)):
    #     infos[i].printScreen(display,newInfo[i],font)


def printObjects(objects,display):
    for object in objects:
        object.printScreen(display)


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)
def end():
    #GPIO.cleanup()
    pygame.quit()
    sys.exit(0)



def main():
    process=Process()
    process.mainScreen()



if __name__ == "__main__":

    
    signal.signal(signal.SIGINT, signal_handler)

    
    main()