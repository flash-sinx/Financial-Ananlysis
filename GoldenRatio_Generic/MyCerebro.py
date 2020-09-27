# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 08:52:00 2020

@author: shivanshu bohara
"""
#%%
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
# Import the backtrader platform
import backtrader as bt
import GoldenRatio
import LogFile
import matplotlib.pyplot as plt

if __name__ == '__main__':    
    
    StartDate = datetime.datetime(2015, 1, 9, 9, 15, 00)
    EndDate = datetime.datetime(2019, 12, 24, 15, 25, 00)
    TF1 = bt.TimeFrame.Minutes
    Comp1 = 5
    TF2 = bt.TimeFrame.Days
    Comp2 = 1 
    InitialValue = 2500000
    Leverage = 1
    Commission = 0.00008 * Leverage
    PrintBrief = True
    DevelopReport = False
    DrawPlots = True
    ShowPlots = False
    DataPath = 'banknifty5min.csv'
    Strategy = 'GoldenRatio'
    Stock = 'BankNifty'
    
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    # Add a strategy and change the parameters of strategy according to wish
    cerebro.addstrategy(GoldenRatio.GoldenRatio, Leverage = Leverage, StopLoss = 0.0065)
    
    # Create a Data Feed
    data = bt.feeds.GenericCSVData(
        dataname=DataPath,
        fromdate=StartDate,
        todate=EndDate,
        timeframe = TF1,
        compression = Comp1,
        dtformat = ('%Y-%m-%d %H:%M:%S'),
        datetime = 0,
        open = 1,
        high = 2,
        low = 3,
        close = 4,
        volume = 5,
        openinterest = -1)
    
    cerebro.adddata(data)
    cerebro.resampledata(data, timeframe=TF2, compression=Comp2)
    # Add the Data Feed to Cerebro
    
    # Set our desired cash start
    #cerebro.broker.set_slippage_perc(perc = 0.01, slip_open=True)
    cerebro.broker.set_coc(True)
    cerebro.broker.setcash(InitialValue)
    cerebro.broker.setcommission(commission=Commission,mult=Leverage)
  
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name = 'returnsmonthly', timeframe=bt.TimeFrame.Months)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name = 'returnsyearly', timeframe=bt.TimeFrame.Years)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
    cerebro.addanalyzer(bt.analyzers.Transactions)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Years)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addanalyzer(bt.analyzers.TimeDrawDown, timeframe=bt.TimeFrame.Months)
   
    # Run over everything
    results = cerebro.run()
    strat0 = results[0]
    FinalValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % FinalValue)
    if DrawPlots and ShowPlots:
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 100
        fig_size[1] = 75
        plt.rcParams["figure.figsize"] = fig_size
        cerebro.plot(style ='candlebars')
    
    if DrawPlots and not ShowPlots:
        cerebro.saveplots(style ='candlebars', file_path = 'grplot.png')
    
    
    TotalMarketData = len(open(DataPath).readlines(  ))
    logger = LogFile.Log(strat0, Stock, Strategy, StartDate, EndDate, InitialValue, FinalValue, DrawPlots, TotalMarketData, Leverage, ShowPlots)
    logger.getanalysis()
    logger.docalc()
    if PrintBrief:
        logger.PrintBrief()
    if DevelopReport:
        logger.DevelopReport()
    