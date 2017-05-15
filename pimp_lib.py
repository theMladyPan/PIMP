from Tkinter import *
from ttk import *
from PIL import Image
import PIL, ImageTk, random, os
from tkFileDialog import askopenfilename, asksaveasfilename
from math import log
from multiprocessing import Process, Queue, cpu_count

EDGE_MASK=( (0,-1,0),(-1,4,-1),(0,-1,0) )
LAPLACIAN_MASK=EDGE_MASK
GAUSS_BLUR_MASK=( (.05,.15,.05),(.15,.2,.15),(.05,.15,.05) )
MOTION_X_BLUR_MASK=( (0,0,0),(1/3.0,1/3.0,1/3.0),(0,0,0) )
MOTION_Y_BLUR_MASK=( (0,1/3.0,0),(0,1/3.0,0),(0,1/3.0,0) )
SHARPEN_MASK=( (-1,-1,-1),(-1,9,-1),(-1,-1,-1) )
EMBOSS_MASK = ( (-.5,-1,0),(-1,0,1),(0,1,.5) )
SOBEL_X_MASK = ( (-1,0,1),(-3,0,3),(-1,0,1) )
SOBEL_Y_MASK = ( (1,3,1),(0,0,0),(-1,-3,-1) )
    
MEAN = 0
MEDIAN = 1

class MultiP(Process):
    def __init__(self, ID, queue, image, funct):
        self.queue=queue
        Process.__init__(self)
        
        self.image=image
        self.func=funct
        self.ID=ID
        self.start()
    def run(self):
		
        self.queue.put([self.ID, self.func(self.image)])
        self.queue.put([self.ID, chr(0)])
		
		
def dummy_func(text):
    "only dummy function"
    return text*2
		
def multiproc(image, funct):
    cores=cpu_count()
    "use all cores to make transformation"
    queue=Queue()
    
    obr2=Image.new(image.mode, image.size)
    width,height = image.size
    fract=height/cores
        
    for i in range(cpu_count()):
        print i, fract*i, fract*(i+1)
        
        MultiP(i, queue, image.crop((0,fract*i,1024,fract*(i+1))), funct)
            	
        
    while cores:
        result=queue.get()
        if result[1]==chr(0):
            cores-=1
        else:
            print cores*fract
            obr2.paste(result[1],(0,result[0]*fract))
        
    return obr2

def median(values):
    "return median of list 'values'"
    values.sort()
    if len(values)%2==1:
        return values[len(values)/2]
    else:
        return float((values[len(values)/2]+values[(len(values)/2)-1])/2.0)
        
class Dialog:
    def __init__(self, otazka="Are you sure?", nazov="?"):

        self.main=Tk()
        self.main.title(nazov)
        Label(self.main, text=otazka).grid(row=0, columnspan=2, sticky="wens")
        ano=Button(self.main, text="Yes", command=self.yes)
        ano.grid(row=1, column=0, sticky="wens")
        nie=Button(self.main, text="No", command=self.no)
        nie.grid(row=1, column=1, sticky="wesn")
        self.main.mainloop()
    
    def yes(self):
        self.vystup=True
        self.main.destroy()

    def no(self):
        self.vystup=False
        self.main.destroy()

    def get(self):
        return self.vystup

def openImage(source_file):
    return Image.open(source_file)

def resize(obr, width=1024, height=0):
        if height:
            return obr.resize((width, height), Image.ANTIALIAS)
        else:
            ratio=obr.size[0]/float(obr.size[1])
            return obr.resize((width, int(width/ratio)), Image.ANTIALIAS)

def toGrey(obr):
    return obr.convert("L")
    
def invert(obr):
    "invert each pixel value of loaded image"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    for x in range(obr.size[0]):
        for y in range(obr.size[1]):
            if obr.mode=="L":
                pxn[x,y]=256-pxo[x,y]
            elif obr.mode=="RGB":
                pxn[x,y]=(256-pxo[x,y][0],256-pxo[x,y][1],256-pxo[x,y][2])
    
    return obr2
    
def stepify(obr, step):
    "convert values to fixed steps"
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    if obr.mode=="L":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=(pxo[x,y]/step)*step
                
    elif obr.mode=="RGB":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=((pxo[x,y][0]/step)*step,(pxo[x,y][1]/step)*step,(pxo[x,y][2]/step)*step)
                
    return obr2
    
def treshold(obr, treshold=None):
    "bitify pixel values from treshold to 1, else 0"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    data=obr.histogram()
    if treshold==None:
        treshold=data.index(max(data))
        
    if obr.mode=="L":    
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=255*(pxo[x,y]/treshold)
                
    elif obr.mode=="RGB":    
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=((pxo[x,y][0]/treshold)*255,(pxo[x,y][1]/treshold)*255,(pxo[x,y][2]/treshold)*255)
                
    return obr2
    
def save(obr, destination=False):
    "save the current state of the image"
    if destination:
        obr.save(destination)
    else:
        main=Tk()
        obr.save(asksaveasfilename(initialfile="image", defaultextension=".jpg", filetypes=[("JPEG",".jpg"),("PNG",".png"),("BMP",".bmp"),("TIF",".tif")]))
        main.destroy()
        
def equalize(obr):
    "equalize the map of values in histogram"
    
    if obr.mode=="L":
        obr2=Image.new(obr.mode, obr.size)
        pxn=obr2.load()
        pxo=obr.load()
        
        data=obr.histogram()
        data_total=sum(data)
        data_256=data_total/256
        rozdelenie=dict()
        i=0
        novy=0
        for n in range(256):
            novy+=data[n]
            if novy>=data_256:
                i+=novy/data_256
                novy=novy-(novy/data_256)*data_256
            rozdelenie[n]=i
            
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=rozdelenie[pxo[x,y]]
        return obr2 
    
    elif obr.mode=="RGB":
        return merge(equalize(disintegrate(obr)[0]),equalize(disintegrate(obr)[1]),equalize(disintegrate(obr)[2]))
    
def logarithm(obr):
    "apply logarithmic function to each pixel, enlightens the dark places over bright background"
    
    if obr.mode=="L":
        obr2=Image.new(obr.mode, obr.size)
        pxn=obr2.load()
        pxo=obr.load()
        values=[]
        
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                values.append(pxo[x,y])
        c=255/(log(1+max(values)))
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                pxn[x,y]=c*log(pxo[x,y]+1)
        return obr2
    
    elif obr.mode=="RGB":
        return merge(logarithm(disintegrate(obr)[0]),logarithm(disintegrate(obr)[1]),logarithm(disintegrate(obr)[2]))
    
def exponential(obr, koef=1.2):
    "darkens the overexposed places if koef>1, else serves mostly like logarithm"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    for x in range(obr.size[0]):
        for y in range(obr.size[1]):
            if obr.mode=="L":
                pxn[x,y]=(pxo[x,y])**koef
            elif obr.mode=="RGB":
                pxn[x,y]=(pxo[x,y][0]**koef,pxo[x,y][1]**koef,pxo[x,y][2]**koef)
                    
    return obr2   
    
def adaptiveTreshold(obr, method=MEAN, bias=0):
    "5x5 adaptive treshold useful for tresholding image with uneven lightning"
    
    if obr.mode=="L":
        obr2=Image.new(obr.mode, obr.size)
        pxn=obr2.load()
        pxo=obr.load()
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                try:
                    if method==MEDIAN:
                        treshold=int(median([pxo[x-2,y-2],pxo[x-1,y-2],pxo[x,y-2],pxo[x+1,y-2],pxo[x+2,y-2],
                              pxo[x-2,y-1],pxo[x-1,y-1],pxo[x,y-1],pxo[x+1,y-1],pxo[x+2,y-1],
                              pxo[x-2,y]  ,pxo[x-1,y]  ,pxo[x,y]  ,pxo[x+1,y]  ,pxo[x+2,y],
                              pxo[x-2,y+1],pxo[x-1,y+1],pxo[x,y+1],pxo[x+1,y+1],pxo[x+2,y+1],
                              pxo[x-2,y+2],pxo[x-1,y+2],pxo[x,y+2],pxo[x+1,y+2],pxo[x+2,y+2]]))
                    else: 
                        treshold=(pxo[x-2,y-2]+pxo[x-1,y-2]+pxo[x,y-2]+pxo[x+1,y-2]+pxo[x+2,y-2]+
                              pxo[x-2,y-1]+pxo[x-1,y-1]+pxo[x,y-1]+pxo[x+1,y-1]+pxo[x+2,y-1]+
                              pxo[x-2,y]  +pxo[x-1,y]  +pxo[x,y]  +pxo[x+1,y]  +pxo[x+2,y]+
                              pxo[x-2,y+1]+pxo[x-1,y+1]+pxo[x,y+1]+pxo[x+1,y+1]+pxo[x+2,y+1]+
                              pxo[x-2,y+2]+pxo[x-1,y+2]+pxo[x,y+2]+pxo[x+1,y+2]+pxo[x+2,y+2])/25

                    if (pxo[x,y]+bias)>treshold: pxn[x,y]=255
                    else: pxn[x,y]=0
                except IndexError: pass
    
    elif obr.mode=="RGB":
        return merge(adaptiveTreshold(disintegrate(obr)[0],method=method, bias=bias),adaptiveTreshold(disintegrate(obr)[1],method=method, bias=bias),adaptiveTreshold(disintegrate(obr)[2],method=method, bias=bias))
                
    return obr2
    
def mask(obr, m, bias=0, k=1):
    "apply the 3x3 'm' mask to loaded image and applying bias to that image"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    if obr.mode=="RGB":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                try:
                    pxn[x,y]= ( int(( m[0][0]*pxo[x-1,y-1][0] +m[0][1]*pxo[x,y-1][0] +m[0][2]*pxo[x+1,y-1][0] +\
                                      m[1][0]*pxo[x-1,y][0]   +m[1][1]*pxo[x,y][0]   +m[1][2]*pxo[x+1,y][0]   +\
                                      m[2][0]*pxo[x-1,y+1][0]   +m[2][1]*pxo[x,y+1][0] +m[2][2]*pxo[x+1,y+1][0] )*k+bias) ,
                                int(( m[0][0]*pxo[x-1,y-1][1] +m[0][1]*pxo[x,y-1][1] +m[0][2]*pxo[x+1,y-1][1] +\
                                      m[1][0]*pxo[x-1,y][1]   +m[1][1]*pxo[x,y][1]   +m[1][2]*pxo[x+1,y][1]   +\
                                      m[2][0]*pxo[x-1,y+1][1]   +m[2][1]*pxo[x,y+1][1] +m[2][2]*pxo[x+1,y+1][1] )*k+bias) ,
                                int(( m[0][0]*pxo[x-1,y-1][2] +m[0][1]*pxo[x,y-1][2] +m[0][2]*pxo[x+1,y-1][2] +\
                                      m[1][0]*pxo[x-1,y][2]   +m[1][1]*pxo[x,y][2]   +m[1][2]*pxo[x+1,y][2]   +\
                                      m[2][0]*pxo[x-1,y+1][2]   +m[2][1]*pxo[x,y+1][2] +m[2][2]*pxo[x+1,y+1][2] )*k+bias) )
                           
                except IndexError:
                    pass
    elif self.im.mode=="L":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                try:
                    pxn[x,y]=   m[0][0]*pxo[x-1,y-1] +m[0][1]*pxo[x,y-1] +m[0][2]*pxo[x+1,y-1] +\
                                m[1][0]*pxo[x-1,y]   +m[1][1]*pxo[x,y]   +m[1][2]*pxo[x+1,y]   +\
                                m[2][0]*pxo[x-1,y]   +m[2][1]*pxo[x,y+1] +m[2][2]*pxo[x+1,y+1] +bias
                except:
                    pass
                
    return obr2
    
def histogram(obr):
    "plot out the histogram of image"
    
    data=obr.histogram()
    data_max=float(max(data))
    main2=Tk()
    main2.title("Histogram, image %s, mode %s, from %d to %d"%(obr.size,obr.mode, min(data), data_max))
    main=Frame(main2)
    main.pack(fill=BOTH, expand=1)
    
    if obr.mode=="RGB":
        board=Canvas(main, width=770, height=256)
        for i in range(768):
            board.create_line(i+2,256,i+2,256-(data[i]/data_max)*256, fill="red")
            
    elif obr.mode=="L":
        board=Canvas(main, width=514, height=512)
        for i in range(512):
            board.create_line(i+2,512,i+2,512-(data[i/2]/data_max)*512, fill="red")
    else:
        print "unknown type %s"%obr.mode
            
    board.pack(fill=BOTH, expand=1)
    Button(main, text="Close", command=main2.destroy).pack(fill=BOTH, expand=1)
    main2.mainloop()
    
def disintegrate(obr):
    r, g, b = obr.split()
    return [r,g,b]

def merge(r,g,b):
    return Image.merge("RGB", (b, g, r))
    
def noise(obr, koeff=0.5):
    "apply random noise over image with koefficient 'koeff' from <0,1>"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    for x in range(obr.size[0]):
        for y in range(obr.size[1]):
            if obr.mode=="L":
                pxn[x,y]=pxo[x,y]+int((random.random()*2-1)*koeff*255)
            elif obr.mode=="RGB":
                pxn[x,y]=(int(pxo[x,y][0]+(random.random()*2-1)*koeff*255),
                          int(pxo[x,y][1]+(random.random()*2-1)*koeff*255),
                          int(pxo[x,y][2]+(random.random()*2-1)*koeff*255))
    
    return obr2

def medianFilter(obr):
    "apply median filter over image"
    
    obr2=Image.new(obr.mode, obr.size)
    pxn=obr2.load()
    pxo=obr.load()
    
    if obr.mode=="L":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                try:
                    pxn[x,y]=int(median([pxo[x-1,y-1],pxo[x,y-1],pxo[x+1,y-1],
                                     pxo[x-1,y],  pxo[x,y],  pxo[x+1,y],
                                     pxo[x-1,y+1],pxo[x,y+1],pxo[x+1,y+1]]))
                except IndexError: pass
                
    elif obr.mode=="RGB":
        for x in range(obr.size[0]):
            for y in range(obr.size[1]):
                try:
                    pxn[x,y]=(int(median([pxo[x-1,y-1][0],pxo[x,y-1][0],pxo[x+1,y-1][0],
                                     pxo[x-1,y][0],  pxo[x,y][0],  pxo[x+1,y][0],
                                     pxo[x-1,y+1][0],pxo[x,y+1][0],pxo[x+1,y+1][0]])),
                              int(median([pxo[x-1,y-1][1],pxo[x,y-1][1],pxo[x+1,y-1][1],
                                     pxo[x-1,y][1],  pxo[x,y][1],  pxo[x+1,y][1],
                                     pxo[x-1,y+1][1],pxo[x,y+1][1],pxo[x+1,y+1][1]])),
                              int(median([pxo[x-1,y-1][2],pxo[x,y-1][2],pxo[x+1,y-1][2],
                                     pxo[x-1,y][2],  pxo[x,y][2],  pxo[x+1,y][2],
                                     pxo[x-1,y+1][2],pxo[x,y+1][2],pxo[x+1,y+1][2]])))
                
                except IndexError: pass
    return obr2

def show(obr, title="Peek"):
    main=Tk()
    main.title(title)
    image = ImageTk.PhotoImage(obr)
    canvas = Canvas(main,width=obr.size[0],height=obr.size[1])
    canvas.create_image(obr.size[0]/2,obr.size[1]/2,image=image)
    canvas.pack()
    main.mainloop()
        
if __name__ == "__main__":
    show(multiproc(openImage("obr.JPG"),adaptiveTreshold))
