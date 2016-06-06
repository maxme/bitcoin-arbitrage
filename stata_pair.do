cd "/Users/phil/work/bitcoin-arbitrage/"

insheet using "HaobtcCNY1.csv", clear
sort timestamp
save "HaobtcCNY1.dta", replace

insheet using "HaobtcCNY.csv", clear
//append using "HaobtcCNY1.dta"

sort timestamp
save "HaobtcCNY.dta", replace

format %13.0f timestamp

line price timestamp, yaxis(1) || connected cny timestamp, yaxis(2) || connected btc timestamp, yaxis(3)
//twoway (line btc timestamp ) (scatter btc timestamp )
//twoway (line cny timestamp ) (scatter cny timestamp ) 
//(line diff3 timestamp ) (scatter diff3 timestamp ) (line diff4 timestamp ) (scatter diff4 timestamp ) 
//twoway (rconnected stratumantpoolcom stratumf2poolcom stratumantpoolcom)
