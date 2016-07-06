 
namespace go trade_service
namespace py trade_service

const string EX_INTERNAL_ERROR = "trader internal error";
const string EX_PRICE_OUT_OF_SCOPE = "price is out of scope";
const string EX_NO_USABLE_FUND  = "no usable exchange fund  by now";
const string EX_NO_USABLE_DEPTH = "no usable exchange depth by now";
const string EX_TRADE_QUEUE_FULL = "trade queue is full";
const string EX_DEPTH_INSUFFICIENT = "exchange depth is insufficient";
const string EX_PRICE_NOT_SYNC = "price is not in tickers";
const string EX_EXIST_ERROR_ORDERS = "exist error status orders";


exception TradeException {
	1: string reason,
}

struct ExchangeStatus {
	1: bool canbuy,
	2: bool cansell,
}

struct ExchangeConfig{
	1: string exchange,
	2: string access_key,
	3: string secret_key,
}

struct AmountConfig{
	1: double max_cny,
	2: double max_btc,
}

struct Account  {
	1: string exchange ,
	2: double available_cny ,
	3: double available_btc ,
	4: double frozen_cny    ,
	5: double frozen_btc    ,
	6: bool   pause_trade,
}

struct Ticker {
	1: double ask,
	2: double bid,
}

struct Trade{
	1: string client_id,
	2: double amount,
	3: double price,
}


enum TradeType{
	BUY,
	SELL,
}

enum OrderStatus{
	TIME_WEIGHTED,
	SPLIT,
	READY,
	ORDERED,
	SUCCESS,
	ERROR,
	CANCELED,
	MATCH
}


struct TradeOrder {
	1:i64 			id                  
	2:i64 			site_order_id
	3:string 		exchange  
	4:double		price         
	5:TradeType    	trade_type        
	6:OrderStatus  	order_status,      
	7:double 		estimate_cny       
	8:double 		estimate_btc       
	9:double 		estimate_price
	10:double 		deal_cny           
	11:double 		deal_btc          
	12:double		deal_price     
	13:double		price_margin       
	14:string 		order_id             
	15:string		created
	16:string		update_at                      
	17:i64			try_times 
	18:string		info  
	19:string		memo
	20:i64			match_id             
}

service TradeService {
	oneway void 		ping(),
	oneway void  		config_keys(1: list<ExchangeConfig> exchange_configs),
	oneway void  		config_amount(1: AmountConfig amount_config),
	ExchangeStatus   	get_exchange_status(), 
	void				check_price(1:double price, 2:TradeType trade_type) throws (1:TradeException tradeException), 
	void   				buy(1:Trade trade) throws (1:TradeException tradeException), 
	void   				sell(1:Trade trade) throws (1:TradeException tradeException),
	Ticker 				get_ticker(),
	list<Account> 		get_account(),
	void				get_alert_orders() throws (1:TradeException tradeException) //client  will retry every minute, then send email/sms
}
//save all depth 
