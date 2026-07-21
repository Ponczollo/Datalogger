# Database

```bash
sudo docker build -t datalogger-db database
sudo docker run --name datalogger-db -p 5432:5432 -e POSTGRES_DB=datalogger -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres datalogger-db
```