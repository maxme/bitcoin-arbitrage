cd "/Users/phil/work/bitcoin-arbitrage/trade_history"

insheet using "HaobtcCNY1.csv", clear
sort timestamp
save "HaobtcCNY1.dta", replace

insheet using "HaobtcCNY2.csv", clear
sort timestamp
save "HaobtcCNY2.dta", replace

insheet using "HaobtcCNY4.csv", clear
sort timestamp
save "HaobtcCNY4.dta", replace

insheet using "HaobtcCNY.csv", clear
//append using "HaobtcCNY2.dta"
//append using "HaobtcCNY1.dta"
append using "HaobtcCNY4.dta"

sort timestamp
save "HaobtcCNY.dta", replace

gen datetime = timestamp*1000 + Clock("1 Jan 1970", "DMY")+ Clock("08:00", "hm")
format %tCHH:MM:SS datetime

line price datetime in -2000/-1, yaxis(1) || connected cny datetime in -2000/-1, yaxis(2) || connected btc datetime in -2000/-1, yaxis(3)

//twoway (line btc timestamp ) (scatter btc timestamp )
//twoway (line cny timestamp ) (scatter cny timestamp ) 
//(line diff3 timestamp ) (scatter diff3 timestamp ) (line diff4 timestamp ) (scatter diff4 timestamp ) 
//twoway (rconnected stratumantpoolcom stratumf2poolcom stratumantpoolcom)
