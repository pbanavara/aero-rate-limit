### A simple python web app to test Aerospike quotas

#### Usage
Run `http://localhost:8000/docs ` to load Starlette documentation for the APIs

#### To set quotas 
`http://localhost:8000/admin/tps` From the Starlette documentaiton URL

#### To test rate limits
`ab -p input.txt -T application/json -c 50 -n 100 http://127.0.0.1:8000/data`
where input.txt contains your JSON payload




