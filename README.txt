------------------------------------------------------------------------------------------------------
COMMAND TO SET UP RUNNING ENVIRONMENT
------------------------------------------------------------------------------------------------------
python -m da configure_nodes/configure_nodes.da config/system.properties

------------------------------------------------------------------------------------------------------
COMMAND TO RUN APPLICATION ON THE CONFIGURED ENVIRONMENT
------------------------------------------------------------------------------------------------------
python -m da -n Main -f –-logfilename logs/Main.log -L info src/Master.da config/system.properties

--------------------------------------------------------------------------------------------------------
DESIGN DISCUSSION
--------------------------------------------------------------------------------------------------------
1. Running environment is set up using the source file "configure_nodes/configure_nodes.da"
    - configures master, client and coordinator nodes
    - For each application instance, following nodes are started:
		- 1 master node
		- 1 client node
		- multiple coordinator nodes as specified in the configuration file

2. Application is instantiated using source file "src/Master.da"
	- It contains the main method to run the application
	- It contains the Master code which is used for creating, setting up and starting client, coordinator and their dedicated workers on the respective nodes.
	- Number of instances of various processes started are read from the configuration file
	- Exit mechanism to exit the setup: when client receives the result of all the requests, it requests the master for termination. As soon as the master receives such termination requests from all the clients, it terminates all the processes it had started at the beginning.

3. Client of the application is emulated using "src/Client.da"
	- This process emulate the behaviour of client for our application
	- Its main functions includes:
		- Request generation based on client workload specified in configuration file
		- Determines whether the request is read or update request
		- If the request is update request, then which object is being updated using a data-structure "Information Map"
		- Information-map is a data-structure that maintains the mapping between past requests and the object updated by them
		- Based on the object that is to be updated, it determines the coordinator where the request should be forwarded first
		- Requests are forwarded to respective coordinators in a sequential fashion i.e., a client forwards next request only when it recieves the result of previous request.

4. Coordinator process emulated using "src/Coordinator.da"
	- Any coordinator can act as both - subject as well as resource coordinator
	- All coordinator resides are residing on different nodes (single machine in this implementation)
	- dedicated workers of a coordinator are deployed on the same node as coordinator. This saves latency by having to send a local message from worker to coordinator in case of update request instead of sending
	- Request forwarded by the client is received by the coordinator responsible for read only object
	- For read request, this order does not matter as both the objects are read-only.
	- For consistency, we have followed the order (subject->resource) for read-only requests.
	- For update requests, client predicts the same and sends the request on respective coordinator
	- Once coordinator receives request from the client -
		- determines the object which is to be handled by it.
		- Proactive approach for starvation prevention is followed and if there are any pending read-write request for any of the attribute to be used by this request, the request awaits till pending read-write requests are completed and pending write queue becomes empty.
		- Assigns a unique global Id to the request
		- Assigns a timestamp to the request
		- determines the definitely read and might read attributes for the read only object of this request
		- updates read timestamps of the definitely read attributes of read only object that are to be read during the evaluation of this request.
		- piggybacks the cached updates on to the request object
		- determines the second coordinator responsible to evaluate the request
		- if second coordinator is same as current coordinator : method to handle second object is involved. Thus, reduces latency.
		- if second coordinator is different then a non-local message is sent from current coordinator for further processing.
	- When second coordinator receives message from first coordinator, it updates the read timestamps of the second object and adds itself to the pending might read queue for this object's attributes as required.
	- piggybacks the cached updates on to the request object
	- it then assigns a worker to this request and forwards the request to worker through a local message.
	- Once worker returns the result of request evaluation, coordinator checks the conflicts before committing the updates piggybacked by the worker.
	- Restart the request in case of conflict detection and new timestamp is assigned to the request.
	- commit the updates if no conflicts and send the result to client
	- In parallel to sending result to client, it sends a copy of updates done in this request to the other coordinator

5. Worker process emulated using "src/Worker.da"
	- Deployed on the same node as its coordinator
	- receives request from coordinator 2
	- have access to policy documet.
	- takes authorization decision for this request based on the rules defined in policy
	- For read-request:
		- Unlike decat+, since result is sent directly to the client, this reduces the latency for read request by a significant factor as compared to latency in decat+ implementation
		- In parallel to sending result to client, it sends an asynchronous message to the coordinators with a copy of timestamps updated in this request
	- For update request:
		- checks if the prediction made by client for the update object is true or false
		- if true, it sends the result to coordinator 2 (on the same node as this worker) through a local message
		- if false, it sends the result to coordinator 1 (usually on a different node) though a non-local message
6. Database emulation is done by using "src/Database.da"


Other files:
6. system.properties:
	- It contains properties being used to bring up the complete setup and data required for running the system.
7. policy.xml
	- It contains the policy data in the form of xml which is used by the worker for policy evaluation.
8. resource_data.csv and subject_data.csv : files containing resource and subject data respectively used as a part of database emulator

--------------------------------------------------------------------------------------------------------
ASSUMPTIONS
--------------------------------------------------------------------------------------------------------
1. Database is distributed ie., each node has its own copy
2. Non-local messages: messages sent by a process deployed on one node to a process deployed on another node on the same machine
3. Local Messages: messages sent by a process on a node to a process deployed on the same node
4. latency of local message < latency of non=local message (even when nodes are configured on the same machine)

--------------------------------------------------------------------------------------------------------
LIMITATIONS
--------------------------------------------------------------------------------------------------------
1. All nodes are configured on the same machine
2. All client processes deployed on same node to maintain simplicity
3. Most of the data is kept static due to environment constraints i.e., referred pre-specified values instead of determining them dynamically
4. A single database process is running on the machine but it is assumed that the database is running on every node of the distributed application

--------------------------------------------------------------------------------------------------------
CONTRIBUTIONS
--------------------------------------------------------------------------------------------------------
The contribution stated below is just an approximate division of work between the team members.
Most part of the code has been worked upon by both the team members and the below segregation should not be treated for clear work boundaries.

PseudoCode - Aviral
configure_nodes.da [Multiple Node Implementation] - Swarnima
Master - Swarnima
Client - Swarnima
Coordinator - Aviral and Swarnima
Worker - Aviral
MVCC Database - Aviral
policy.xml - Aviral
README - Swarnima
Performance Evaluation - Swarnima
Testing.txt - Aviral
Test Cases Implementation - Aviral