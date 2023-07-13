#import RPi.GPIO as GPIO
import time
import signal                   
import sys
import pygame
import serial
import SmartFarmControl
import numpy as np

TEMP_LIMIT=3.0
HUMID_LIMIT=20.0
SOIL_LIMIT=20.0
INFO_ICON_SIZE=(150,90)
NOTIFICATION_SIZE=(370,370)
POT_GRID=(3,4)

#import SmartFarmControl
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
    def printInfo(self):
        return str(self.critical)+" "+str(self.temp)

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

class potGridInfo():
    def __init__(self,grid=POT_GRID):
        self.grid=grid
        self.PotInfos=[potInfo(True,Info((False,25,"Good"))) for i in range(grid[0]*grid[1])]
        for i in range(grid[1]):
            self.PotInfos[i].updatePotInfo(False,None)
    def returnPotGridInfo(self,pos):
        return self.PotInfos[pos[0]*self.grid[1]+pos[1]].returnPotInfo()
    def printPotGridInfo(self):
        return "aaaa"
    def updatePotGridInfo(self,orig,dest):
        info=self.PotInfos[orig[0]*self.grid[0]+orig[1]]
        self.PotInfos[dest[0]*self.grid[0]+dest[1]]=potInfo(info.potBool,info.infos)
        self.PotInfos[orig[0]*self.grid[0]+orig[1]].updatePotInfo(False,None)
    


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
    def calculateColor(self):
        color=Color()
        # if self.name=="temp":
        #     self.color=
        
        # if self.unit=="humid":
        #     self.color=

        # if self.unit=="vent":
        #     if 
        #     self.color=

        # if self.unit=="soil":
        #     self.color=
        
    def printScreen(self,display,info,font):
        self.updateInfo(info)
        self.calculateColor()
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
                self.info=str(self.info)

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
        if self.info is None:
            text=font.render("No Pot Selected",True,color.gray)
            text_rect=text.get_rect()
            text_rect.center=self.pos
            display.blit(text,text_rect)
        else:
            temp=self.info.temp
            status=self.info.status
            
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
        self.info=info
    def updateClick(self,display,mouse):
        if self.pos[0] + self.size[0]/2.0 > mouse[0] > self.pos[0]-self.size[0]/2.0 and self.pos[1] + self.size[1]/2.0 > mouse[1] > self.pos[1]-self.size[1]/2.0:
            if self.action is not None:
                    time.sleep(0.2)
                    self.action()
    def interaction(self,display,mouse):
        return


class potGrid:
    def __init__(self,pos,size,thickness,radius,potGridInfo, action = None):
        self.pos=pos
        self.action=action
        self.size=size
        self.thickness=thickness
        self.radius=radius
        self.potGridInfo=potGridInfo

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
                return False,None,None,None
            else:
                potBool,info=self.potGridInfo.returnPotGridInfo(grid)
                if potBool:
                    return False,info,None,None
                else:
                    return False,None,None,None
        elif self.action=="selection":
            if grid is None:
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
                    return False,info,None,None
                        


    def updatePotGridInfo(self,potGridInfo):
        self.potGridInfo=potGridInfo
    def drawPotGrid(self):
        color=Color()
        potGridIcon = pygame.Surface(NOTIFICATION_SIZE)
        potGridIcon.fill(color.white)
        if self.selection:
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
                    potBool,_=self.potGridInfo.returnPotGridInfo((i,j))
                    if potBool:
                        col=color.gray
                    else:
                        col=color.green
                    if i==self.selectedPot[0] and j==self.selectedPot[1]:
                        col=color.yellow
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
                    potBool,_=self.potGridInfo.returnPotGridInfo((i,j))
                    if potBool:
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

        self.arduino = serial.Serial('/dev/ttyACM0', 115200)

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

        self.farmControl=SmartFarmControl.SmartFarmControl()
        self.farmControl.initializing_origin()

        self.info=[25.0,50.0,0,0,0,False]
        self.potGridInfo=potGridInfo(POT_GRID)

    def updateSensorsInfos(self):
        self.arduino.flushInput()
        line = self.arduino.readline()
        line = line.decode('euc-kr') # cp949 euc-kr utf-8
        line = line.split()
        for i in range(5):
            self.info[i]=line[i]

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
        potSelectionIcon.blit(plantIcon,(NOTIFICATION_SIZE[0]/2.0-85,NOTIFICATION_SIZE[1]/2.0-85))
        potSelectionButton=Button(potSelectionIcon,(1024-280,260),potSelectionIcon,self.potSelectionScreen)
        notification=Notification(None,(280,260),NOTIFICATION_SIZE,15,20,"main",self.notificationScreen)

        buttons=[self.stopButton,self.settingsButton,potSelectionButton]
        self.infos=[temp,humidity,ventilation,soilHumidity]

        # printInfos(infos,self.screen,info,self.font)
        # printObjects(buttons,self.screen)
        count=0
        while True:
            count+=1
            if count%100==0:
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
        potgrid=potGrid((1024-280,260),NOTIFICATION_SIZE,15,20,self.potGridInfo,"disabled")
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[potgrid]
        
        count=0
        while True:
            count+=1
            if count%100==0:
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
        potgrid=potGrid((280,260),NOTIFICATION_SIZE,15,20,self.potGridInfo,"selection")
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[potgrid]

        count=0
        while True:
            count+=1
            if count%100==0:
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
                    if move:
                        print(orig)
                        print(dest)
                        self.farmControl.moveMotorsOrigDest(orig,dest)
                        self.potGridInfo.updatePotGridInfo(orig,dest)
                        notification.updateInfo(None) 
                        

            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def settingsScreen(self):
        backIcon=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(50,50))
        clickBack=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(40,40))

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)
        buttons=[self.stopButton,self.settingsButton,backButton]

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
    infos[0].printScreen(display,newInfo[0],font) #temp
    infos[1].printScreen(display,newInfo[1],font) #humidity
    infos[2].printScreen(display,newInfo[5],font) #ventilation
    infos[3].printScreen(display,newInfo[3],font) #soil
    # for i in range(len(infos)):
    #     infos[i].printScreen(display,newInfo[i],font)


def printObjects(objects,display):
    for object in objects:
        object.printScreen(display)


def signal_handler(sig, frame):
    #GPIO.cleanup()
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