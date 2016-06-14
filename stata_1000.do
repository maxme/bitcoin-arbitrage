cd "/Users/phil/work/bitcoin-arbitrage/trade_history"

insheet using "HaobtcCNY4.csv", clear
sort timestamp
save "HaobtcCNY4.dta", replace

insheet using "HaobtcCNY.csv", clear
//append using "HaobtcCNY4.dta"

sort timestamp
save "HaobtcCNY.dta", replace

gen datetime = timestamp*1000 + Clock("1 Jan 1970", "DMY")+ Clock("08:00", "hm")
format %tCHH:MM:SS datetime

graph twoway line price datetime, yaxis(1) || connected cny datetime, yaxis(2) || connected btc datetime, yaxis(3)
|| ,saving(figure_profit)

//line price datetime in -1000/-1, yaxis(1) || connected cny datetime in -1000/-1, yaxis(2) || connected btc datetime in -1000/-1, yaxis(3)
