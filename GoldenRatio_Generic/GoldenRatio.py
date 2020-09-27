# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 17:27:51 2020

@author: shivanshu bohara
"""
#%%
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
# Import the backtrader platform
import backtrader as bt
import math

class GoldenRatio(bt.Strategy):
    sharelot = 10
    allowedtrade = 0
    # 0 means all allowed
    # 1 means long not allowed
    # 2 means short not allowed
    params = (
            ('SL', True),
            ('StopLoss', 0.005),
            ('sessionstart', datetime.time(9,15,00)),
            ('mytime', datetime.time(9,20,00)),
            ('lastorder', datetime.time(15,0,00)),
            ('squareofftime', datetime.time(15,5,00)),
            ('FibRatio', 0.618),
            ('PrintTransaction', False),
            ('Leverage', 1),
            ('LotSize', 20),
            ('SingleEntryInaDir', True)
            )
    
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        if self.params.PrintTransaction:
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.minopen = self.datas[0].open
        self.dayopen = self.datas[1].open
        self.minhigh = self.datas[0].high
        self.dayhigh = self.datas[1].high
        self.minlow = self.datas[0].low
        self.daylow = self.datas[1].low
        self.minclose = self.datas[0].close
        self.dayclose = self.datas[1].close
        self.LongLevel = 0
        self.ShortLevel = 0
        self.stop_price=0
        self.SLorder = None
        self.ActualLotSize = self.params.LotSize/self.params.Leverage
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                if self.position and self.params.SL:
                    self.stop_price = order.executed.price*(1-self.params.StopLoss)
                    self.log('STOP LOSS CREATE, %.2f' % self.stop_price)
                    self.SLorder = self.close(size = self.sharelot, exectype=bt.Order.Stop, price=self.stop_price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
                if self.position and self.params.SL:
                    self.stop_price = order.executed.price*(1+self.params.StopLoss)
                    self.log('STOP LOSS CREATE, %.2f' % self.stop_price)
                    self.SLorder = self.close(size = self.sharelot, exectype=bt.Order.Stop, price=self.stop_price)
            elif order.isclose():
                self.log('CLOSE EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        #Check cancellation
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        #Add trade finances
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    
    def next(self):
        currtime = self.datas[0].datetime.time(0)
        
        if(currtime==self.params.mytime):
            YesterdayHigh = self.dayhigh[0]
            YesterdayLow = self.daylow[0]
            First10minHigh = max(self.minhigh[0],self.minhigh[-1])
            First10minLow = min(self.minlow[0],self.minlow[-1])
            YesterdayRange = YesterdayHigh - YesterdayLow
            Rangeoffirst10min = First10minHigh - First10minLow
            RangeFactor = YesterdayRange + Rangeoffirst10min
            GoldenValue = self.params.FibRatio * RangeFactor
            self.LongLevel = self.dayclose[0] + GoldenValue
            self.ShortLevel = self.dayclose[0] - GoldenValue
            
        if(currtime>self.params.sessionstart and currtime<self.params.lastorder):
            if not self.position:
                if self.minclose[0]>=self.LongLevel:
                    if(self.params.SingleEntryInaDir==False or (self.params.SingleEntryInaDir==True and self.allowedtrade!=1)):
                        self.log('BUY CREATE, %.2f' % self.minclose[0])
                        self.sharelot = self.ActualLotSize*math.floor(self.broker.getcash()/(self.minclose[0]*self.ActualLotSize))
                        self.order = self.buy(size = self.sharelot)
                        self.allowedtrade = 1
                                        
                elif self.minclose[0]<=self.ShortLevel:
                    if(self.params.SingleEntryInaDir==False or (self.params.SingleEntryInaDir==True and self.allowedtrade!=2)):
                        self.log('SELL CREATE, %.2f' % self.minclose[0])
                        self.sharelot = self.ActualLotSize*math.floor(self.broker.getcash()/(self.minclose[0]*self.ActualLotSize))
                        self.order = self.sell(size = self.sharelot)
                        self.allowedtrade = 2
                
        elif(currtime==self.params.squareofftime):
            self.allowedtrade = 0
            if self.position:
                self.broker.cancel(self.SLorder)
                self.log('CLOSE CREATE, %.2f' % self.minclose[0])
                self.order = self.close(size = self.sharelot)  
