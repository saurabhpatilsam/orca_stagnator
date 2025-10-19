You can connect to **Redis** via `redis-cli`
```
redis-cli -h marketdatafeed.eastus.redis.azure.net -p 10000 -a '<REDIS_PASSWORD>' --tls -c
```
And then subscribe to a price stream for the market instrument using the command: `SUBSCRIBE <feed>` where feed can be:
- TRADOVATE_NQU5_PRICE
- TRADOVATE_MNQU5_PRICE
- TRADOVATE_ESU5_PRICE
- TRADOVATE_MESU5_PRICE
