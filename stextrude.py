'''
t parametric extrusion
we assume we return to staring point ( circular path )

This script handles parametric functions (x,y,z)(t), and extrudes a
cross-sectional function (x,y)(s). Both functions are assumed to be
periodic, and you must mantually make sure that the ranges close.

.stl output has been tested. call as :

python stextrude.py output.stl


'''
from math import *
from numpy import *
import sys,os

fx="cos(t)+0.5*cos(t/2)"       #function defining x(t)
fy="sin(t)+0.5*sin(t/2)"       #function defining y(t)
fz="sin(3*t)*0.1+sin(t/2)"     #function defining z(t)

cx='0.1*cos(s)'       #function defining x cross-section(t)
cy='0.1*sin(s)'       #function defining t cross-section(t)

stlmode = True        #.stl if true else .scad
use_file = False      # file or stdout ?
filename = 'untitled' #default file name

res = 300             #resolution of extrusion path
cres = 80             #resolution of cross-section
tmin = 0              #t starting value
tmax = 4*pi           #t ending value
smin = 0              #s starting value
smax = 2*pi           #s ending value

if len(sys.argv)>1: 
	if 'help' in sys.argv[1]:
		print "I didn't write any help yet"
		exit(0)
	if '.stl'==sys.argv[1][-4:]:
		sys.stderr.write("using stl file mode\n")
		use_file = True
		stlmode = True
		filename = sys.argv[1]
	if '.scad'==sys.argv[1][-5:]:
		sys.stderr.write("using scad file mode\n")
		use_file = True
		stlmode = False
		filename = sys.argv[1]

def xyzevaluate(t):
	x=eval(fx)
	y=eval(fy)
	z=eval(fz)
	return array([x,y,z])
	
def xyevaluate(s):
	x=eval(cx)
	y=eval(cy)
	return array([x,y])

def mag(a): 
	return sqrt(sum(a*a))

def unit(a):
	m=mag(a)
	if m>0:
		return a/m
	return a

S = array(range(cres))*(smax-smin)/cres+smin
T = array(range(res))*(tmax-tmin)/res+tmin
p = [xyzevaluate(t) for t in T]

crosssection = matrix([xyevaluate(t) for t in S])

x0 = array([p[-1]]+p[:-1])
x1 = array(p)
x2 = array(p[1:]+[p[0]])
d1 = x0-x1
d2 = x2-x1

normals = array([ unit(cross(a,b)) for a,b in zip(d1,d2)])
pn1     = array([ unit(cross(a,b)) for a,b in zip(normals,d2)])
pn2     = array([-unit(cross(a,b)) for a,b in zip(normals,d1)])
paranormals = map(unit,(pn1+pn2)*0.5)
basis = map(matrix,zip(normals,paranormals))

#print shape(basis[0]),shape(crosssection)
shell = [crosssection*basis[i]+p[i] for i in xrange(res)]

sys.stderr.write("%s\n"%([shape(shell)]))

points = []
triangles = []
for i in xrange(res):
	for j in xrange(cres):
		points.append(list(array(shell[i][j])[0]))
		p1=i*cres+j
		p2=i*cres+(j+1)%cres
		p3=(i+1)%res*cres+j
		p4=(i+1)%res*cres+(j+1)%cres
		triangles += [[p1,p2,p4],[p1,p4,p3]]

#print p
#print normals
#print T
#print paranormals
#print shape(shell)

data = ''
if stlmode:
	'''
	solid name
	facet normal ni nj nk
	  outer loop
	    vertex v1x v1y v1z
	    vertex v2x v2y v2z
	    vertex v3x v3y v3z
	  endloop
	endfacet
	endsolid name
	'''	
	import time
	t = time.localtime()
	name = 'object%s%s%s%s%s%s'%(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
	data+= 'solid %s\n'%name
	for facet in triangles:
		#try:
		p=[array(points[f]) for f in facet]
		#except IndexError:
		#	sys.stderr.write(str(facet)+"\n")
		point=unit(cross(p[1]-p[0],p[2]-p[0]))
		#point=unit(cross(p[0]-p[2],p[2]-p[1]))
		#point=[0,0,0]
		data+='facet normal %s\n'%' '.join(map(str,point))
		data+='  outer loop\n'
		#if inward_wall:
		p=[p[0],p[2],p[1]]
		for point in p:
			data+= '    vertex %s\n'%' '.join(map(str,point))
		data+= '  endloop\n'
		data+= 'endfacet\n'
	data+= 'endsolid %s\n'%name
else:
	tos = lambda f:"%0.7f"%f		
	maptos = lambda a:'['+','.join(map(tos,a))+']'
	mapmaptos = lambda a:'['+','.join(map(maptos,a))+']'
	data="polyhedron(\npoints=\n%s,\ntriangles\n=%s);"%(mapmaptos(points),triangles)

if use_file:
	f = open(filename, "w")
	f.write(data)
	f.close()
	os.system("meshlab %s"%filename)	
else:
	print data

g = open("%s.source"%filename,'w')
g.write("%s\n%s\n%s\n"%(fx,fy,fz))
g.close()
		


