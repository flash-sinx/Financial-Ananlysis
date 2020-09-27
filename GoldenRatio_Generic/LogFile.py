# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 09:18:28 2020

@author: shivanshu bohara
"""
#%%
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# Import the backtrader platform
import math
import matplotlib.pyplot as plt
from numpy import mean
from statistics import stdev
from statistics import median
import numpy as np

class Log(object):
    def __init__ (self, strat, stock, strategy, startdate, enddate, initialvalue, finalvalue, drawplots, totalmarketdata, leverage, showplots):
        self.strat0 = strat
        self.Stock = stock
        self.Strategy = strategy
        self.StartDate = startdate
        self.EndDate = enddate
        self.InitialValue = initialvalue
        self.FinalValue = finalvalue
        self.DrawPlots = drawplots
        self.TotalMarketData = totalmarketdata
        self.Leverage = leverage
        self.ShowPlots = showplots
        delta = enddate-startdate
        self.TotalDays = delta.days
        self.TotalMonths = self.TotalDays/30.42
        self.TotalYears = self.TotalDays/365.25
        
    def getanalysis(self):
        self.timereturnsmonthly = self.strat0.analyzers.returnsmonthly.get_analysis()
        self.timereturnsyearly = self.strat0.analyzers.returnsyearly.get_analysis()
        self.tradeanalysis = self.strat0.analyzers.tradeanalyzer.get_analysis()
        self.transactions = self.strat0.analyzers.transactions.get_analysis()
        self.drawdown = self.strat0.analyzers.drawdown.get_analysis()
        self.returns = self.strat0.analyzers.returns.get_analysis()
        self.sharperatio = self.strat0.analyzers.sharperatio.get_analysis()
        self.sqn = self.strat0.analyzers.sqn.get_analysis()
        self.monthlydrawdown = self.strat0.analyzers.timedrawdown.get_analysis()
        
    def wrtiecsv(self):
        import csv
        with open("godenratio.csv", "w", newline='') as outfile:
            csvwriter = csv.writer(outfile)
            for key,value in self.tradeanalysis.items():
                csvwriter.writerow((key,value))
        
    def docalc(self):
        self.TotalTrades = self.tradeanalysis['total']['total']
        self.TotalWon = self.tradeanalysis['won']['total']
        self.TotalLost = self.tradeanalysis['lost']['total']
        self.WinStreak = self.tradeanalysis['streak']['won']['longest']
        self.LossStreak = self.tradeanalysis['streak']['lost']['longest']
        self.TotalLong = self.tradeanalysis['long']['total']
        self.TotalShort = self.tradeanalysis['short']['total']
        self.WinPercent = 100*self.TotalWon/(self.TotalWon+self.TotalLost)
        self.GrossProfit = self.tradeanalysis['won']['pnl']['total']
        self.GrossLoss = self.tradeanalysis['lost']['pnl']['total']
        self.ProfitFactor = self.GrossProfit/abs(self.GrossLoss)
        self.MaxProfit = self.tradeanalysis['won']['pnl']['max']
        self.MaxLoss = self.tradeanalysis['lost']['pnl']['max']
        self.AvgWin = self.tradeanalysis['won']['pnl']['average']
        self.AvgLoss = self.tradeanalysis['lost']['pnl']['average']
        self.AvgLong = self.tradeanalysis['long']['pnl']['average']
        self.AvgShort = self.tradeanalysis['short']['pnl']['average']
        self.PayOffRatio = self.AvgWin/abs(self.AvgLoss)
        self.AvgProfit = self.tradeanalysis['pnl']['net']['average']
        self.NetProfit = self.tradeanalysis['pnl']['net']['total']
        self.AvgLen = self.tradeanalysis['len']['average']
        self.WinLen = self.tradeanalysis['len']['won']['average']
        self.LossLen = self.tradeanalysis['len']['lost']['average']
        self.TotalLen = self.tradeanalysis['len']['total']
        self.MaxDD = self.drawdown['max']['drawdown']
        self.MaxMonthlyDD = self.monthlydrawdown['maxdrawdown']
        self.MaxDDlen = math.ceil(self.drawdown['max']['len']/75)
        self.SharpeRatio = self.sharperatio['sharperatio']
        self.SQN = self.sqn['sqn']
        self.TotalProfitPercent = (self.FinalValue-self.InitialValue)*100/self.InitialValue
        self.CAGR = self.returns['rnorm100']
        self.DrawDown = 0
        self.RunUp = 0
        self.MaxRunUp = 0
        self.dates_toplot = [self.StartDate]
        self.portfolio_value_toplot = [self.InitialValue]
        self.DailyReturns = []
        self.PercentTimeInMarket = self.TotalLen*100/self.TotalMarketData
        self.PessimisticCAGR = (((1+((self.AvgWin*(self.TotalWon-math.sqrt(self.TotalWon)) + self.AvgLoss*(self.TotalLost+math.sqrt(self.TotalLost)))/self.InitialValue))**(1/self.TotalYears))-1)*100
        self.RiskReward = self.TotalProfitPercent/self.MaxDD
        self.ModelEfficiency = self.NetProfit*100/self.GrossProfit
        
    def PrintBrief(self):
        print()
        print(self.Stock)
        print("Start Date: ", self.StartDate)
        print("End Date: ", self.EndDate)
        print("Net Profit: ",self.NetProfit)
        print("CAGR: ",self.CAGR,"%")
        print("Shapre Ratio: ", self.SharpeRatio)
        print("SQN: ", self.SQN)
        print("MaxDD: ", self.MaxDD,"%")
        print("Percent Time in Market: ", self.PercentTimeInMarket, "%")
        print("Pessimistic CAGR: ",self.PessimisticCAGR,"%")
        print("Risk Reward Ratio: ", self.RiskReward)
    
    def DevelopReport(self):
        import xlsxwriter
        workbook = xlsxwriter.Workbook(self.Strategy+'SL_'+self.Stock+'.xlsx')
        bold = workbook.add_format({'bold': True})
        format2 = workbook.add_format({'num_format': 'yyyy'})
        format3 = workbook.add_format({'num_format': 'mmm-yy'})
        format4 = workbook.add_format({'num_format': 'dd-mm-yy'})
        format5 = workbook.add_format({'num_format': 'hh:mm:ss'})
        returns = workbook.add_worksheet('Returns')
        returns.write(0,0,'Year', bold)
        returns.write(0,1,'% Returns', bold)
        i=1
        for key,value in self.timereturnsyearly.items():
            returns.write(i,0,key,format2)
            returns.write(i,1,value*100)
            i += 1
        i+=2
        returns.write(i,0,'Month', bold)
        returns.write(i,1,'% Returns', bold)
        i+=1
        for key,value in self.timereturnsmonthly.items():
            returns.write(i,0,key,format3)
            returns.write(i,1,value*100)
            i += 1
        
        j = 3
        k = 2
        analysis = workbook.add_worksheet('Analysis')
        analysis.set_column('C:C', 30)
        analysis.write(j-1,k,'Stats', bold)
        analysis.write(j-1,k+1,'Data', bold)
        analysis.write(j,k,'Total Trades')
        analysis.write(j,k+1,self.TotalTrades)
        analysis.write(j+1,k,'Total Won')
        analysis.write(j+1,k+1,self.TotalWon)
        analysis.write(j+2,k,'Total Lost')
        analysis.write(j+2,k+1,self.TotalLost)
        analysis.write(j+3,k,'Win percentage', bold)
        analysis.write(j+3,k+1,self.WinPercent, bold)
        analysis.write(j+4,k,'Net Profit')
        analysis.write(j+4,k+1,self.NetProfit)
        analysis.write(j+5,k,'Total Profit%')
        analysis.write(j+5,k+1,self.TotalProfitPercent)
        analysis.write(j+6,k,'CAGR', bold)
        analysis.write(j+6,k+1,self.CAGR, bold)
        analysis.write(j+7,k,'Longet Win Streak')
        analysis.write(j+7,k+1,self.WinStreak)
        analysis.write(j+8,k,'Longest Loss Streak', bold)
        analysis.write(j+8,k+1,self.LossStreak, bold)
        analysis.write(j+9,k,'Gross Profit')
        analysis.write(j+9,k+1,self.GrossProfit)
        analysis.write(j+10,k,'Gross Loss')
        analysis.write(j+10,k+1,self.GrossLoss)
        analysis.write(j+11,k,'Profit Factor')
        analysis.write(j+11,k+1,self.ProfitFactor)
        analysis.write(j+12,k,'Max Profit in 1 trade')
        analysis.write(j+12,k+1,self.MaxProfit)
        analysis.write(j+13,k,'Max Loss in 1 trade', bold)
        analysis.write(j+13,k+1,self.MaxLoss, bold)
        analysis.write(j+14,k,'Average Profit in winning trade')
        analysis.write(j+14,k+1,self.AvgWin)
        analysis.write(j+15,k,'Average Loss in losing trade')
        analysis.write(j+15,k+1,self.AvgLoss)
        analysis.write(j+16,k,'Average Profit in long trade')
        analysis.write(j+16,k+1,self.AvgLong)
        analysis.write(j+17,k,'Average Profit in short trade')
        analysis.write(j+17,k+1,self.AvgShort)
        analysis.write(j+18,k,'Average Profit in a trade', bold)
        analysis.write(j+18,k+1,self.AvgProfit, bold)
        analysis.write(j+19,k,'PayOff Ratio')
        analysis.write(j+19,k+1,self.PayOffRatio)
        analysis.write(j+20,k,'Average Length')
        analysis.write(j+20,k+1,self.AvgLen)
        analysis.write(j+21,k,'Average Winning Length')
        analysis.write(j+21,k+1,self.WinLen)
        analysis.write(j+22,k,'Average Losing Length')
        analysis.write(j+22,k+1,self.LossLen)
        analysis.write(j+23,k,'Max DrawDown percent', bold)
        analysis.write(j+23,k+1,self.MaxDD, bold)
        analysis.write(j+24,k,'Max DrawDown Length in days')
        analysis.write(j+24,k+1,self.MaxDDlen)
        analysis.write(j+25,k,'Max Monthly DrawDown')
        analysis.write(j+25,k+1,self.MaxMonthlyDD)
        analysis.write(j+26,k,'Sharpe Ratio', bold)
        analysis.write(j+26,k+1,self.SharpeRatio, bold)
        analysis.write(j+27,k,'SQN', bold)
        analysis.write(j+27,k+1,self.SQN, bold)
        analysis.write(j+28,k,'Percent Time in Market', bold)
        analysis.write(j+28,k+1,self.PercentTimeInMarket, bold)
        analysis.write(j+29,k,'Pessimistic CAGR', bold)
        analysis.write(j+29,k+1,self.PessimisticCAGR, bold)
        analysis.write(j+30,k,'Risk Reward Ratio')
        analysis.write(j+30,k+1,self.RiskReward)
        analysis.write(j+31,k,'Model Efficiency')
        analysis.write(j+31,k+1,self.ModelEfficiency)
        
        graph = workbook.add_worksheet('Graph')
        graph.insert_image('A0', 'grplot.png')
        
        tradelog = workbook.add_worksheet('Trade Log')
        tradelog.write(0,0,'Entry Date', bold)
        tradelog.write(0,1,'Entry Time', bold)
        tradelog.write(0,2,'Position', bold)
        tradelog.write(0,3,'Price', bold)
        tradelog.write(0,4,'Quantity', bold)
        tradelog.write(0,5,'Cost', bold)
        tradelog.write(0,6,'Exit Date', bold)
        tradelog.write(0,7,'Exit Time', bold)
        tradelog.write(0,8,'Price', bold)
        tradelog.write(0,9,'Quantity', bold)
        tradelog.write(0,10,'Return', bold)
        tradelog.write(0,11,'Profit', bold)
        tradelog.write(0,12,'%Profit', bold)
        tradelog.write(0,13,'DrawDown(in %)', bold)
        tradelog.write(0,14,'RunUp(in %)', bold)
        i=0
        buy = 0
        for key,value in self.transactions.items():
            if(i%2==0):
                tradelog.write((int)(i/2+1),0,key,format4)
                tradelog.write((int)(i/2+1),1,key,format5)
                if(value[0][0]>0):
                    tradelog.write((int)(i/2+1),2,'Long')
                else:
                    tradelog.write((int)(i/2+1),2,'Short')
                tradelog.write((int)(i/2+1),3,value[0][1])
                tradelog.write((int)(i/2+1),4,value[0][0]*self.Leverage)
                buy = value[0][4]
                tradelog.write(i/2+1,5,value[0][4])
            else:
                tradelog.write((int)((i+1)/2),6,key,format4)
                self.dates_toplot.append(key)
                tradelog.write((int)((i+1)/2),7,key,format5)
                tradelog.write((int)((i+1)/2),8,value[0][1])
                tradelog.write((int)((i+1)/2),9,value[0][0]*self.Leverage)
                tradelog.write((int)((i+1)/2),10,value[0][4])
                profitintrade = (value[0][4]+buy)*self.Leverage
                self.portfolio_value_toplot.append(self.portfolio_value_toplot[-1]+profitintrade)
                tradelog.write((int)((i+1)/2),11,profitintrade)
                percentprofit = profitintrade*100/abs(buy)
                self.DailyReturns.append(percentprofit)
                tradelog.write((int)((i+1)/2),12,percentprofit)
                self.DrawDown = min(0,(((1+self.DrawDown/100)*(1+percentprofit/100))-1)*100)
                tradelog.write((int)((i+1)/2),13,self.DrawDown)
                self.RunUp = max(0,(((1+self.RunUp/100)*(1+percentprofit/100))-1)*100)
                tradelog.write((int)((i+1)/2),14,self.RunUp)
                if self.RunUp>self.MaxRunUp:
                    self.MaxRunUp = self.RunUp
            i+=1
        Wins = []
        Losses = []
        for d in self.DailyReturns:
            if d>=0:
                Wins.append(d)
            else:
                Losses.append(d)
        self.AvgWinpercent = mean(Wins)
        self.AvgLosspercent = mean(Losses)
        self.MedianWinpercent = median(Wins)
        self.MedianLosspercent = median(Losses)
        self.StdevWinpercent = stdev(Wins)
        self.StdevLosspercent = stdev(Losses)
        self.AvgProfitPercent = mean(self.DailyReturns)
        self.StdError = stdev(self.DailyReturns)
        j = j+1
        analysis.write(j+32,k,'Avg Profit Percent', bold)
        analysis.write(j+32,k+1,self.AvgProfitPercent, bold)
        analysis.write(j+33,k,'Avg Win Percent', bold)
        analysis.write(j+33,k+1,self.AvgWinpercent, bold)
        analysis.write(j+34,k,'Avg Loss Percent', bold)
        analysis.write(j+34,k+1,self.AvgLosspercent, bold)
        analysis.write(j+35,k,'Median Win Percent')
        analysis.write(j+35,k+1,self.MedianWinpercent)
        analysis.write(j+36,k,'Median Loss Percent')
        analysis.write(j+36,k+1,self.MedianLosspercent)
        analysis.write(j+37,k,'Stdev Win Percent')
        analysis.write(j+37,k+1,self.StdevWinpercent)
        analysis.write(j+38,k,'Stdev Loss Percent')
        analysis.write(j+38,k+1,self.StdevLosspercent)
        analysis.write(j+39,k,'Standard Error')
        analysis.write(j+39,k+1,self.StdError)
        
        j+=2
        analysis.write(j+39,k,'After Removing 2% of the extreme trades')
        Wins.sort()
        Losses.sort()
        Nonextremewins = Wins[:int(len(Wins) *.98)]
        Nonextremelosses = Losses[int(len(Losses) * .02):]
        analysis.write(j+40,k,'Avg Win Percent')
        analysis.write(j+40,k+1,mean(Nonextremewins))
        analysis.write(j+41,k,'Avg Loss Percent')
        analysis.write(j+41,k+1,mean(Nonextremelosses))
        
        
        years_toplot = []
        years_value_toplot = []
        for d in self.timereturnsyearly.keys():
            years_toplot.append(d.year)
        for v in self.timereturnsyearly.values():
            years_value_toplot.append(v*100)
        
        if self.DrawPlots:
            fig_size = plt.rcParams["figure.figsize"]
            fig_size[0] = 6
            fig_size[1] = 4.5
            plt.rcParams["figure.figsize"] = fig_size
            fig = plt.figure()
            plt.bar(years_toplot, years_value_toplot, color='red')
            plt.title('Yearly Returns(in %)')
            plt.savefig('yearlyreturns.png')
            returns.insert_image('F3', 'yearlyreturns.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
        returns.write(0,2,'Average', bold)
        returns.write(1,2,mean(years_value_toplot))
        returns.write(0,3,'StDev', bold)
        returns.write(1,3,stdev(years_value_toplot))
        
        
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 10
        fig_size[1] = 7.5
        plt.rcParams["figure.figsize"] = fig_size
        months_toplot = []
        months_value_toplot = []
        quarters_toplot = []
        quarters_value_toplot = []
        quarter_value = 0
        for key,value in self.timereturnsmonthly.items():
            months_toplot.append(str(key.month)+"/"+str(key.year))
            months_value_toplot.append(value*100)
            if(key.month==3 or key.month==6 or key.month==9 or key.month==12):
                quarter_value = (((1+quarter_value/100)*(1+value))-1)*100
                quarters_value_toplot.append(quarter_value)
                quarters_toplot.append(str(key.month)+"/"+str(key.year))
                quarter_value = 0
            quarter_value = (((1+quarter_value/100)*(1+value))-1)*100
        
        if self.DrawPlots:
            fig = plt.figure()
            plt.xticks(rotation = 'vertical')
            plt.bar(months_toplot, months_value_toplot, color='green')
            plt.subplots_adjust(bottom = 0.16, left = 0.05, right = 0.98)
            plt.title('Monthly Returns(in %)')
            plt.savefig('monthlyreturns.png')
            returns.insert_image('F27', 'monthlyreturns.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
        returns.write(len(years_value_toplot)+3,2,'Average', bold)
        returns.write(len(years_value_toplot)+4,2,mean(months_value_toplot))
        returns.write(len(years_value_toplot)+3,3,'StDev', bold)
        returns.write(len(years_value_toplot)+4,3,stdev(months_value_toplot))
        
        if self.DrawPlots:
            fig_size = plt.rcParams["figure.figsize"]
            fig_size[0] = 10
            fig_size[1] = 7.5
            plt.rcParams["figure.figsize"] = fig_size
            fig = plt.figure()
            plt.xticks(rotation = 'vertical')
            plt.bar(quarters_toplot, quarters_value_toplot, color='orange')
            plt.title('Quarterly Returns(in %)')
            plt.savefig('quarterlyreturns.png')
            returns.insert_image('F65', 'quarterlyreturns.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
        
        if self.DrawPlots:
            fig_size = plt.rcParams["figure.figsize"]
            fig_size[0] = 10
            fig_size[1] = 7.5
            plt.rcParams["figure.figsize"] = fig_size
            fig = plt.figure()
            plt.plot(self.dates_toplot,self.portfolio_value_toplot)
            plt.title('Portfolio Value')
            plt.savefig('Portfolio.png')
            returns.insert_image('F101', 'Portfolio.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
        
        if self.DrawPlots:
            import seaborn
            fig, ax = plt.subplots(figsize =(9, 7)) 
            seaborn.violinplot(ax = ax,  y = self.DailyReturns ) 
            plt.title('Distribution of Retruns in a trade')
            plt.savefig('violinplot.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
            Distribution = workbook.add_worksheet('Distribution')
            Distribution.insert_image('C4', 'violinplot.png')
            
            startyear = self.StartDate.year
            endyear = self.EndDate.year
            array = np.zeros((endyear-startyear+1,12), dtype=int)
            for date in self.dates_toplot:
                array[date.year-startyear][date.month-1] += 1
            fig,ax = plt.subplots(figsize=(8.5,(endyear-startyear+1)*0.65))
            years_toplot = []
            for i in range(endyear-startyear+1):
                years_toplot.append(startyear+i)
            seaborn.heatmap(array, annot=True, cmap = "Greens", yticklabels = years_toplot, xticklabels = ['Jan','Feb','Mar','Apr','May','June','July','Aug','Sept','Oct','Nov','Dec'], ax=ax)    
            plt.title('Distribution of no. of Trades')
            plt.savefig('heatmap.png')
            if self.ShowPlots:
                plt.show()
            else:
                plt.close(fig)
            Distribution.insert_image('C40', 'heatmap.png')
            
        workbook.close()    