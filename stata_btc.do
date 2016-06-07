cd "/Users/phil/work/bitcoin-arbitrage/trade_history"

insheet using "HaobtcCNY.csv", clear
sort timestamp
save "HaobtcCNY.dta", replace

format %13.0f timestamp

//line btc timestamp, yaxis(1) || line cny timestamp, yaxis(2) 
twoway (line btc timestamp ) (scatter btc timestamp )
//twoway (line cny timestamp ) (scatter cny timestamp ) 
//(line diff3 timestamp ) (scatter diff3 timestamp ) (line diff4 timestamp ) (scatter diff4 timestamp ) 
//twoway (rconnected stratumantpoolcom stratumf2poolcom stratumantpoolcom)
