cd "/Users/phil/work/bitcoin-arbitrage/trade_history"

insheet using "HaobtcCNY0.csv", clear
sort timestamp
save "HaobtcCNY0.dta", replace

insheet using "HaobtcCNY1.csv", clear
sort timestamp
save "HaobtcCNY1.dta", replace

insheet using "HaobtcCNY2.csv", clear
sort timestamp
save "HaobtcCNY2.dta", replace

insheet using "HaobtcCNY3.csv", clear
sort timestamp
save "HaobtcCNY3.dta", replace

insheet using "HaobtcCNY4.csv", clear
sort timestamp
save "HaobtcCNY4.dta", replace


//insheet using "HaobtcCNY.csv", clear
append using "HaobtcCNY4.dta"
//append using "HaobtcCNY3.dta"
//append using "HaobtcCNY2.dta"
//append using "HaobtcCNY1.dta"
//append using "HaobtcCNY0.dta"

sort timestamp
save "HaobtcCNY.dta", replace

gen datetime = timestamp*1000 + Clock("1 Jan 1970", "DMY")+ Clock("08:00", "hm")
format %tCHH:MM:SS datetime

graph twoway line price datetime, yaxis(1) || connected cny datetime, yaxis(2) || connected btc datetime, yaxis(3)
|| ,saving(figure_profit)

//line price datetime in -500/-1, yaxis(1) || connected cny datetime in -500/-1, yaxis(2) || connected btc datetime in -500/-1, yaxis(3)

