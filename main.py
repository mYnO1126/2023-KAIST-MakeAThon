#import RPi.GPIO as GPIO
import time
import signal                   
import sys
import pygame

TEMP_LIMIT=3.0
HUMID_LIMIT=20.0
SOIL_LIMIT=20.0
INFO_ICON_SIZE=(150,90)
NOTIFICATION_SIZE=(370,370)

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


class Button:
    def __init__(self,img_in,pos, img_act, action = None):
        # mouse = pygame.mouse.get_pos()
        # click = pygame.mouse.get_pressed()
        self.width=img_in.get_width()
        self.height=img_in.get_height()
        self.img_in=img_in
        self.img_act=img_act
        self.pos=pos
        self.action=action
        # if x + width > mouse[0] > x and y + height > mouse[1] > y:
        #     display.blit(img_act,(x_act, y_act))
        #     if click[0] and action != None:
        #         time.sleep(1)
        #         action()
        # else:
        #     display.blit(img_in,(x,y))
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
    def __init__(self,img_in,info,unit,pos,size,thickness,radius,range):
        color=Color()
        self.img=img_in
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
        # if self.unit=="°C":
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
            text=font.render(str(round(self.info,1))+self.unit,True,self.color)
            text_rect=text.get_rect()
            text_rect.center=(self.pos[0]+25,self.pos[1])
        display.blit(text,text_rect)
    


    


class Notification:
    def __init__(self,infos,pos,size,thickness,radius, action = None):
        self.info=infos
        self.pos=pos
        self.size=size
        self.thickness=thickness
        self.radius=radius
        self.action=action
    def printScreen(self,display):
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
    def updateClick(self,display,mouse):
        if self.pos[0] + self.size[0]/2.0 > mouse[0] > self.pos[0]-self.size[0]/2.0 and self.pos[1] + self.size[1]/2.0 > mouse[1] > self.pos[1]-self.size[1]/2.0:
            if self.action is not None:
                    time.sleep(0.2)
                    self.action()
    def interaction(self,display,mouse):
        return


class potGrid:
    def __init__(self,infos,pos,size, action = None):
        self.info=infos
        self.pos=pos
        self.action=action
        self.size=size

    def printScreen(self,display):
        return

    def updateClick(self,display,mouse):
        if self.action=="disabled":
            return
        else:
            return "notification"



class Process:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font=pygame.font.Font('freesansbold.ttf',20)

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



    def mainScreen(self):
        
        self.info=[25.0,50.0,True,50.0]

        tempIcon=pygame.transform.scale(pygame.image.load("images/temp.jpg"),(50,50))
        humidityIcon=pygame.transform.scale(pygame.image.load("images/humidity.png"),(50,50))
        ventilationIcon=pygame.transform.scale(pygame.image.load("images/ventilation.jpg"),(50,50))
        soilHumidityIcon=pygame.transform.scale(pygame.image.load("images/soil-humid.png"),(50,50))
        plantIcon=pygame.transform.scale(pygame.image.load("images/plant.png"),(170,170))
       
        temp=infoIcon(tempIcon,25,"°C",(212-45,520),INFO_ICON_SIZE,10,5,TEMP_LIMIT)
        humidity=infoIcon(humidityIcon,50,"%",(412-15,520),INFO_ICON_SIZE,10,5,HUMID_LIMIT)
        ventilation=infoIcon(ventilationIcon,False,"",(612+15,520),INFO_ICON_SIZE,10,5,0)
        soilHumidity=infoIcon(soilHumidityIcon,50,"%",(812+45,520),INFO_ICON_SIZE,10,5,SOIL_LIMIT)

        potSelectionIcon = pygame.Surface(NOTIFICATION_SIZE)
        potSelectionIcon.fill(self.color.white)
        pygame.draw.rect(
            potSelectionIcon,
            self.color.skyblue,
            pygame.Rect(
                (0,0),
                NOTIFICATION_SIZE,
            ),
            15,
            5,
        )
        potSelectionIcon.blit(plantIcon,(NOTIFICATION_SIZE[0]/2.0-85,NOTIFICATION_SIZE[1]/2.0-85))
        potSelectionButton=Button(potSelectionIcon,(1024-280,260),potSelectionIcon,self.potSelectionScreen)
        notification=Notification(None,(280,260),NOTIFICATION_SIZE,15,5,self.notificationScreen)

        buttons=[self.stopButton,self.settingsButton,potSelectionButton]
        self.infos=[temp,humidity,ventilation,soilHumidity]

        # printInfos(infos,self.screen,info,self.font)
        # printObjects(buttons,self.screen)

        while True:
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            printObjects([notification],self.screen)
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

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)
        notification=Notification(None,(200,200),NOTIFICATION_SIZE,20,3,None)
        #potgrid=potGrid()
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[notification]

        while True:
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            printObjects(objects,self.screen)
            printInfos(self.infos,self.screen,self.info,self.font)
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
                    notification.interaction(self.screen,mouse)
            pygame.display.flip()
            self.fpsClock.tick(self.fps)

    def potSelectionScreen(self):
        backIcon=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(50,50))
        clickBack=pygame.transform.scale(pygame.image.load("images/back_icon.png"),(40,40))

        backButton = Button(backIcon,(920,40),clickBack,self.mainScreen)
        notification=Notification(None,(1024-280,260),NOTIFICATION_SIZE,20,3,None)
        #potgrid=potGrid()
        
        buttons=[self.stopButton,self.settingsButton,backButton]
        objects=[notification]

        while True:
            self.screen.fill(self.color.white)
            mouse = pygame.mouse.get_pos()
            printObjects(objects,self.screen)
            printInfos(self.infos,self.screen,self.info,self.font)
            for button in buttons:
                button.updateMouseOn(self.screen,mouse)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    for button in buttons:
                        button.updateClick(self.screen,mouse)
                    notification.interaction(self.screen,mouse)
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
    for i in range(len(infos)):
        infos[i].printScreen(display,newInfo[i],font)


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