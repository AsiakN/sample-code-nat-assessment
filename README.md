## About Fido Take Home

### TECHNICAL DESIGN FOR A BACKEND SYSTEM CAPABLE OF POWERING A TRANSACTION AND USER INTERACTION SERVICE

### Objective
The goal of this technical design document is to design a backend system capable of powering a transactions and user interactions for fido. Much of the requirements is stated in the “Fido Backend Engineer Home Assignment” document.

### System Architecture
![Blank diagram](https://github.com/AsiakN/fido-nat-assessment/blob/master/system_architecture.png)
A REST API written in FastAPI will feed from MongoDB to serve the external parties.
A strategy for scaling this is to have multiple instances of the REST API and consumer running respectively. That way, our system is optimized for availability. With multiple instances of the REST API running, we introduce a load balancer to ensure that requests are efficiently distributed between all instances of the REST API.

MongoDB is chosen for a few reasons:
- (a) we have all the data we need from the data processed by the api and potentially the data consumed in Kafka. Thus, there’ll most likely be no need for joins to produce transaction data
- (b) We have flexibility on the additional data updates from other processes 


#### Potential Strategies for scaling
- Since asynchronous processing is important for this system, a message streaming platform such as Apache Kafka will sit at the heart of this system. I did not implement that but it is strategy to address how the system connects with other services in the organization
Kafka will receive streams of events from a producer in the REST API app when a transaction record is created or updated. Other producers could potentially be introduced in the system but We’re less worried about the estimated number of producers or messages per day because of Kafka’s ability to handle very large volumes of messages at scale.
Consumers would consume messages from Kafka and create some database records in MongoDB or trigger some other action.
- 
### Technology Stack
- **Message Broker:** Apache Kafka
- **Caching:** Redis
- **Database:** a NoSQL database such as MongoDB
- **REST API:** FastAPI. This is chosen based on what the team is already familiar with. No learning curve involved.


## Setup
- Run `git clone ` to clone this repo
- cd into fido-nat-assessment directory
- copy .env.example file into .env
- Your IDE should activate a virtual environment, if not run :
  - `python3 -m venv venv` to create a virtual virtualenv folder which will contain packages
  - `source venv/bin/activate` for macOS and `venv\Scripts\activate.bat` for Windows
  - 
## Run via Docker
```
Build the docker images
Run >>> docker-compose build <<<

Use this command to run all three containers(Redis, Fastapi, mongodb):
Run >>> docker-compose up <<<
```

## Run manually
- run `pip install -r requirements.txt ` in the application root directory
- run the command `uvicorn main:app --reload --host 0.0.0.0 --port 8989`
- `Redis` and `mongodb` have to be already running on the host machine
