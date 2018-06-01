# -*- coding: utf-8 -*-
"""
Created on Tue Apr 17 19:58:53 2018

@author: Saira, Srijan
"""

from gurobipy import *
import sqlite3
import csv
import multiprocessing as mp

NFL=Model()
NFL = read("OR604 Model File v2.lp")

myVars=NFL.getVars()

games={}
varbounds={}
for v in myVars:
    if v.varName[:2]=='GO':
        games[v.varName]= v
        varbounds[v]=[v.lb,v.ub]

 #looking at every constraint and determine if constraint c is a hard constraint       
myConstrs=NFL.getConstrs()
for c in myConstrs:
    row=NFL.getRow(c)
    myFlag=True
    for r in range(row.size()):#how many variables are in there
        if row.getVar(r).varName[:2]!='GO':
            myFlag=False
            break
    if myFlag:
        if c.sense == '<' and c.RHS == 0:
           for r in range(row.size()):
               row.getVar(r).lb =0
               row.getVar(r).ub = 0
               games[row.getVar(r).varName].lb=0
               games[row.getVar(r).varName].ub=0
               varbounds[row.getVar(r)][0]=0
               varbounds[row.getVar(r)][1]=0
                          
NFL.update()
NFL.write("NFL1.lp")

def modelprober(n):
    n=0
    NFL1 =read("NFL1.lp")
    NFL.setParam('timelimit',10)

    myVars1=NFL1.getVars()

    games={}
    varbounds={}
    for v in myVars1:
        if v.varName[:2]=='GO':
            games[v.varName]= v
            varbounds[v]=[v.lb,v.ub]      
    myFlag=True
    cnt=0
    while myFlag :
        myFlag=False
        for v in varbounds:
            if varbounds[v][0]!=varbounds[v][1] and 'PRIME' in v.varName:
                games[v.varName].lb=1
                games[v.varName].ub=1
                NFL.update()
                NFL.optimize()
                if NFL.status == GRB.INFEASIBLE:
                    games[v.varName].lb=0
                    games[v.varName].ub=0
                    varbounds[v][0]=0
                    varbounds[v][1]=0
                    myFlag=True
                else:
                    games[v.varName].lb=0
                    games[v.varName].ub=1
                    varbounds[v][0]=0
                    varbounds[v][1]=1
                NFL.update()
    return (varbounds, myFlag)

if __name__ == "__main__": 
    poolsize=4
    myPool=mp.Pool(poolsize)
    modelFlag=True
    while modelFlag == True:
        result = myPool.imap_unordered(modelprober,range(0))
        for v in result:
            modelFlag[1]
            varbounds=v[0]
            print (varbounds)
    myPool.close() 
    myPool.join()
    
with open('prime_seed.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    for game in games:
            Key=game.split('_')[1:]
            if 'PRIME' in Key :
                Key.append(games[game].lb)
                Key.append(games[game].ub)  
                writer.writerow(Key)
