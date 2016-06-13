cd "/Users/phil/work/bitcoin-arbitrage/trade_history"


insheet using "arbitrage.csv", clear

sort timestamp
save "arbitrage.dta", replace

gen datetime = timestamp*1000 + Clock("1 Jan 1970", "DMY")+ Clock("08:00", "hm")
format %tCHH:MM:SS datetime

graph twoway line price datetime, yaxis(1) || connected cny datetime, yaxis(2) || connected btc datetime, yaxis(3)
|| ,saving(figure_profit)

//line price datetime in -500/-1, yaxis(1) || connected cny datetime in -500/-1, yaxis(2) || connected btc datetime in -500/-1, yaxis(3)

//twoway (line btc timestamp ) (scatter btc timestamp )
//twoway (line cny timestamp ) (scatter cny timestamp ) 
//(line diff3 timestamp ) (scatter diff3 timestamp ) (line diff4 timestamp ) (scatter diff4 timestamp ) 
//twoway (rconnected stratumantpoolcom stratumf2poolcom stratumantpoolcom)
