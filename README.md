# T2A2 API Webserver - Family Scheduler API

### 1. The problem this app will solve:
Forgot that water bill ? or cant remember the date of that family bbq ? were you invited to your cousins birthday party ?

This problem of forgetting when bills are due to be paid or those family outings you dont want to miss out on, is what this family scheduler app will help solve. It is a scheduler app designed for family members and their family group with two main functions.

**_Please note the terms used for this documentation:_**

**_- member(s) = a family member or members.Eg: Parents & their children._**

**_- Intra group = the immediate family members group._**

**_- Inter group = another external Intra group that has a family relationship._**

### App Main Functions to resolve the problem:
The first function is family members are able to save intra group bill details and when / if they have been paid. All intra group members can add, view and edit bills. Only administrator members can delete bills.

The second function is family members are able to create intra group outings & outings to invite inter groups. These outings can be anything where a family member of their intra group are going / doing something like appointments, meetings, get togethers & holidays. These outings can be marked as private, which means only intra group member(s) will be attending OR outings can be marked as public, which means these outings are for the intra group wanting to invite and participate with other inter groups in the app.

A intra group member can choose which other inter groups to invite to a public outing they have created. Intra groups can view all the public outing invites they have and choose to respond to each particular invite.

### 2. Task management of the SDLC:
For the task management of this application i am using Trello to monitor and apply each task in the development stages of Backlog, In Progress, In Testing, Done & Issues / Rework. For starting the app project all tickets were created and applied to Backlog, then the first ticket of creating a ERd diagram and explanation of features was done & submitted for approval. 
For version control and tracking of changes in the code while developing the app, I am using GitHub and have created a repository which can be located here: [T2A2 Family Scheduler API GitHub repository](https://github.com/smallDazza/T2A2-Webserver/tree/main)
#### Stage 1:
Tasks to explain functions, ERD and start setting up GitHub repo:

![Trello start](./docs/Trello%20-Start.png)
![Trello done ERD](./docs/Trello%20-Start2.png)

#### Stage 2:
For the app IDE I am using VSCode, for the database using PostgreSQL. In progress tickets for setting up these 2 environments + setup a virtual environment and installing the python libraries / modules required:

![Environment setup](./docs/Stage%202.png)

#### Stage 3:
Start with coding the main files located in the src folder and the 5 Models located in the models folder:

![Stage 3](./docs/Stage%203.png)
1[Create Models](./docs/Stage%203.1.png)

#### Stage 4:


