import math

tab=[[0,1,2,2,3,4,5,5,6,7,8,9,11],[2,4,7,10,3,5,3,6,0,11,8,2,6]]

def orient(d,i,j,k):
    a,b,c=(d[0][i],d[1][i]),(d[0][j],d[1][j]),(d[0][k],d[1][k])
    if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])>0:
        return 1
    if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:
        return -1
    if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])==0:
        return 0

print(orient(tab, 0, 1, 2))

def majES(d,SUP,i):
    for j in range(2,i):
        while len(SUP)>1 and orient(d,SUP[-2],SUP[-1],j)!=-1:
            SUP.pop()
        SUP.append(j)
    return SUP

def majEI(d,INF,i):
    for j in range(2,i):
        while len(INF)>1 and orient(d,INF[-2],INF[-1],j)!=1:
            INF.pop()
        INF.append(j)
    return INF

def balayage(d):
    SUP = majES(d, [0, 1], len(d[0]))
    INF = majEI(d, [0, 1], len(d[0]))
    SUP.pop()
    SUP=SUP[1:]
    SUP.reverse()
    
    return INF+SUP

import matplotlib.pyplot as plt
def repEnv(d):
    envelope=balayage(d)
    X = [ tab[0][envelope[i]] for i in range(len(envelope))] + [tab[0][envelope[0]]]

    Y = [ tab[1][envelope[i]] for i in range(len(envelope))] + [tab[1][envelope[0]]]

    plt.plot(tab[0],tab[1],'ro')
    
    plt.plot(X,Y)
    plt.show()


def concave_shape(points, a_min):
    # Convert the minimum angle from degrees to radians
    a_min_radians = math.radians(a_min)
    
    # Call the repEnv function to compute the hull and display it
    repEnv(points, a_min_radians)

    
concave_shape(tab, 45)
    