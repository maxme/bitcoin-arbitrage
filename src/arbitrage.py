import markets
import config

if __name__ == "__main__":
    markets.watch_for_good_op(4, config.callback, config.sleep_time)
