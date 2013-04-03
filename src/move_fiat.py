def get_profit_for(depths, mi, mj, kask, kbid):
    if depths[kask]["asks"][mi]["price"] >= depths[kbid]["bids"][mj]["price"]:
        return 0, 0, 0, 0

    max_amount_buy = 0
    for i in range(mi + 1):
        max_amount_buy += depths[kask]["asks"][i]["amount"]
    max_amount_sell = 0
    for j in range(mj + 1):
        max_amount_sell += depths[kbid]["bids"][j]["amount"]
    max_amount = min(max_amount_buy, max_amount_sell, config.max_tx_volume)

    buy_total = 0
    w_buyprice = 0
    for i in range(mi + 1):
        price = depths[kask]["asks"][i]["price"]
        amount = min(max_amount, buy_total + depths[
                     kask]["asks"][i]["amount"]) - buy_total
        if amount <= 0:
            break
        buy_total += amount
        if w_buyprice == 0:
            w_buyprice = price
        else:
            w_buyprice = (w_buyprice * (
                buy_total - amount) + price * amount) / buy_total

    sell_total = 0
    w_sellprice = 0
    for j in range(mj + 1):
        price = depths[kbid]["bids"][j]["price"]
        amount = min(max_amount, sell_total + depths[
                     kbid]["bids"][j]["amount"]) - sell_total
        if amount < 0:
            break
        sell_total += amount
        if w_sellprice == 0:
            w_sellprice = price
        else:
            w_sellprice = (w_sellprice * (
                sell_total - amount) + price * amount) / sell_total

    profit = sell_total * w_sellprice - buy_total * w_buyprice
    return profit, sell_total, w_buyprice, w_sellprice
