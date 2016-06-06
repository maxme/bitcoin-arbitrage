cd "/Users/phil/work/bitcoin-arbitrage/"

insheet using "HaobtcCNY.csv", clear
sort timestamp
save "HaobtcCNY.dta", replace

format %13.0f timestamp
//twoway (line cny timestamp ) (scatter cny timestamp, sort msize(tiny) lwidth(vvvthin) )
twoway (connected cny timestamp, sort msize(tiny) lwidth(vvvthin))
//twoway (line btc timestamp ) (scatter btc timestamp ) 
//(line diff3 timestamp ) (scatter diff3 timestamp ) (line diff4 timestamp ) (scatter diff4 timestamp ) 
//twoway (rconnected stratumantpoolcom stratumf2poolcom stratumantpoolcom)
