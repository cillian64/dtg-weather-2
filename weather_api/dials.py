"""
Render dials for the frontpage of the weather website

Original by Alastair R. Beresford.  Later modifications in 2016 by David Turner
to move to Python 3 and return dial image as a flask response instead of saving
to a file.
Copyright (C) 2006,2007 Alastair R. Beresford
Copyright (C) 2016 David W. Turner

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
__author__='Alastair R. Beresford'
__copyright__='Copyright (C) 2006 Alastair R. Beresford'
__version__='0.1'

from PIL import Image,ImageDraw, ImageFont
import math
import sys
from datetime import datetime
import get_data
from tzlocal import get_localzone
import pytz
from io import BytesIO
from flask import g, make_response

sensors = {"drybulbtemp": "insttemp",
           "humidity": "insthum",
            "windspeed": "instwindspd",
            "pressure": "instpressure",
            "winddir": "instwinddir",
            "dewpt": "instdewpt"}
units = {"winddir": "deg",
         "windspeed": "knots",
         "drybulbtemp": "C",
         "wetbulbtemp": "C",
         "humidity": "%",
         "pressure": "mBar",
         "cumsunshine": "h",
         "cumrainfall": "mm",
         "dewpt": "C"}

def arrow(im,x,y,r,reading,colour1,colour2,bottom_space,arrow_width=6):
    draw = ImageDraw.Draw(im)
    deg = bottom_space/2+reading*(360-bottom_space)
    theta = deg*2*math.pi/360
    edgex = r*math.sin(theta)+x
    edgey = r*math.cos(theta)+y
    lx = arrow_width*math.sin(theta+math.pi/2)+x
    ly = arrow_width*math.cos(theta+math.pi/2)+y
    rx = arrow_width*math.sin(theta-math.pi/2)+x
    ry = arrow_width*math.cos(theta-math.pi/2)+y
    draw.polygon((lx,ly,edgex,edgey,rx,ry),fill=colour1)
    draw.ellipse((x-arrow_width,y-arrow_width,x+arrow_width,y+arrow_width),fill=colour2)

def dial(im, x, y, r, labels, readings, colours, top=None, bottom=None, ticks_per_label=12, tick_length=10, bottom_space=90):
    """
    Draw a dial on the current image at x, y with radius r
    labels is a tuple or list of values to put on the dial
    reading is a value between 0 and 1
    top is a string placed in the top half of the dial
    bottom is a string placed in the bottom half of the dial
    ticks_per_label is an int representing number of little ticks per label
    bottom_space is the amount of space left between labels at the bottom of the dial
    """
    draw = ImageDraw.Draw(im)
    w = 4
    black = (0,0,0)
    background = (210,240,255)#(255,255,255)
    grey = (128,128,128)
    
    #bounding box for the dial
    x1 = x - r
    x2 = x + r
    y1 = y - r
    y2 = y + r

    #draw outside
    draw.ellipse((x1-1,y1-1)+(x2+1,y2+1),fill=grey)
    draw.ellipse((x1,y1)+(x2,y2),fill=black)
    draw.ellipse((x1+w-1,y1+w-1)+(x2-w+1,y2-w+1),fill=grey)
    draw.ellipse((x1+w,y1+w)+(x2-w,y2-w),fill=background)

    font2 = ImageFont.truetype("sansroman.ttf",8)
    font = ImageFont.truetype("sansbold.ttf",12)

    #draw arrows
    length = r
    for i in range(len(readings)):
        arrow(im,x,y,length,readings[i],colours[i],black,bottom_space)
        length = 2*length/3
        
    #draw index & index labels
    num_ticks = (len(labels)-1)*ticks_per_label+1
    label_count = 0
    for i in range(num_ticks):

        deg = bottom_space/2+i*(360-bottom_space)/(num_ticks-1)
        theta = deg*2*math.pi/360
        if not i%ticks_per_label:
            l = int(tick_length*1.5)
        else:
            l = tick_length
        edgex = r*math.sin(theta)+x
        inx = (r-l)*math.sin(theta)+x
        edgey = r*math.cos(theta)+y
        iny = (r-l)*math.cos(theta)+y
        if not i%ticks_per_label:
            txtw,txth = draw.textsize(labels[label_count],font=font)
            txtx = (r-1.5*l)*math.sin(theta)+x
            txty = (r-1.5*l)*math.cos(theta)+y
          
            draw.text((txtx-txtw/2,txty-txth/2),labels[label_count],font=font,fill=black)
            label_count+=1
        
        draw.line((edgex,edgey)+(inx,iny),fill=black)

    #draw main labels
    if top != None:
        w,h = draw.textsize(top,font=font2)
        draw.text((x-w/2,y-h/2-r/3),top,font=font2,fill=black)
    if bottom != None:
        w,h = draw.textsize(bottom,font=font2)
        if bottom_space < 60:
            draw.text((x-w/2,y-h/2+r/3),bottom,font=font2,fill=black)
        else:
            draw.text((x-w/2,y-h/2+r/1.5),bottom,font=font2,fill=black)

class DialData:
    def __init__(self,x,y,labels,minmaxs,colours,top,ticks_per_label,bottom_space):
        self.x=x
        self.y=y
        self.labels = labels
        self.minmaxs = minmaxs
        self.colours = colours
        self.top = top
        self.bottom = ''
        self.bottom_space = bottom_space
        self.ticks_per_label = ticks_per_label

    def readings(self,value):
        read = []
        for mn,mx in self.minmaxs:
            read += [1-(float(value)-mn)/float(mx-mn)]
        return read

    def bottom_text(self,value,units):
        if isinstance(value,float):
            value = round(value,1)
        self.bottom = str(value)+' '+units

class DialTime(DialData):
    def readings(self,value):
        localt = value
        h, m, s = localt.hour, localt.minute, localt.second
        h = h+m/60.0
        m = m+s/60.0
        
        return (1-(30+m)/60.0,1-(6+h)/12.0)
        pass

    def bottom_text(self,value,units):
        localt = value
        self.top = localt.strftime("%Y-%m-%d")
        self.bottom = localt.strftime("%H:%M:%S")
        

class DialDir(DialData):
    def readings(self,value):
        mn,mx = self.minmaxs[0]
        return (1-float(int(value+180)-mn)/float(mx-mn),)

def sensor_vals():
    cur = g.db.cursor()
    cur.execute("SET SESSION TIME ZONE 'UTC';")
            
    select_sensors = ",".join(sensors[key] for key in sorted(sensors.keys()))
    cur.execute("""SELECT timestamp,{} 
    FROM tblWeatherInstantaneous
    ORDER BY timestamp DESC LIMIT 1;""".format(select_sensors))
    row = cur.fetchone()
    timestamp = pytz.utc.localize(row[0]) # Timestamp in UTC from database
    # Convert timestamp to localtime:
    timestamp = timestamp.astimezone(get_localzone())

    # Put sensor values in the right place for the dials code
    vals = []
    for idx, sensor in enumerate(sorted(sensors.keys())):
        raw = row[idx + 1]
        val = get_data.convert(sensors[sensor])(raw)
        vals.append((sensor, val))
    vals.append(("end", timestamp))

    # Now let's do rainfall and sunshine, both of which are cumulative from
    # midnight.  First, find the current time in utc:
    utcnow = datetime.utcnow()
    # Find midnight utc:
    utcmidnight = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)
    # Now fetch summed rainfall and sunshine since midnight
    # Remember database is in UTC:
    cur.execute("""SELECT sum(instsunshine), sum(instrainfall)
                   FROM tblWeatherInstantaneous
                   WHERE timestamp > %s;""", (utcmidnight,))
    row = cur.fetchone()
    # Add into sensor array for dials code:
    vals.append(("cumsunshine", get_data.convert("instsunshine")(row[0])))
    vals.append(("cumrainfall", get_data.convert("instrainfall")(row[1])))
    return vals

def current_dials():
    # Get the current sensor readings:
    data = sensor_vals()

    # And now let's do some drawing:
    size = 65
    im = Image.new('RGBA',(498,577),(255,255,255,255))

    red = (255,0,0)
    lightred = (255,150,150)
    green = (0,255,0)
    blue = (150,150,255)
    yellow = (255,255,0)
    mustard = (255,200,0)
    purple = (255,100,255)
    
    #find how long cumulative values have been collected
    sincetime = "midnight"
    sunsincetime = "today"

    #assigned anticlockwise
    dials = {'drybulbtemp':DialData(249,100,('40','30','20','10','0','-10'),((-10,40),),(red,),'Temp',10,90),
             'humidity':DialData(120,160,('100','50','0'),((0,100),),(blue,),'Humidity',10,90),
             'windspeed':DialData(80,300,('50','25','0'),((0,50),),(mustard,),'Wind speed',10,90),
             'cumsunshine':DialData(120,440,('24','12','0'),((0,24),),(yellow,),'Sunshine '+sunsincetime,12,90),
             'pressure':DialData(249,500,('1050','1000','950'),((950,1050),),(purple,),'Pressure (QNH)',10,90),
             'cumrainfall':DialData(380,440,('100','50','0'),((0,100),),(blue,),'Rain since '+sincetime,10,90),
             'winddir':DialDir(420,300,('S','E','N','W',''),((0,360),),(green,),'Wind direction',6,0),
             'dewpt':DialData(380,160,('30','20','10','0','-10'),((-10,30),),(blue,),'Dew point',10,90),
             'end':DialTime(249,300,('6','3','12','9',''),((0,59),(0,12)),(red,lightred),'Time',3,0)
             }

    for sensor,value in data:
        if sensor in units:
            u = units[sensor]
        else:
            u = ''

        d = dials[sensor]
        d.bottom_text(value,u)
        dial(im,d.x,d.y,size,d.labels,d.readings(value),d.colours,d.top,d.bottom,d.ticks_per_label,bottom_space=d.bottom_space)

    io = BytesIO()
    im.save(io, 'PNG')
    response = make_response(io.getvalue())
    response.mimetype = 'image/png'
    return response
