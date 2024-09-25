# T2A2 API Webserver - Family Scheduler API

### 1. The problem this app will solve:
Forgot that water bill ? or cant remember the date of that family bbq ? were you invited to your cousins birthday party ?

In Australia if you are late on paying a bill, in particular a credit card or loan, this will affect your financial credit score, even if you forget. Missing just one repayment could drop your credit score by 22%. An American collections company did a survey in 2022 of more than 1100 people and found that 72% were in collections because of non-financial factors, with 32% of this group being because they forgot to pay their bills.

References:

Turner H. 2024. Understanding the Impact of Late Payments on Your Credit Score. [Online]
Available at: https://www.jacarandafinance.com.au/general/impact-of-late-payments-on-your-credit-score/

Lexop. 2022. Consumers are forgetting to pay their bills - here’s how to fix that! [Online]
Available at: https://www.lexop.com/blog/consumers-forgetting-to-pay-bills

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
 - #### Stage 1:
    Tasks to explain functions, ERD and start setting up GitHub repo:

![Trello start](./docs/Trello%20-Start.png)
![Trello done ERD](./docs/Trello%20-Start2.png)

 - #### Stage 2:
    For the app IDE I am using VSCode, for the database using PostgreSQL. In progress tickets for setting up these 2 environments + setup a virtual environment and installing the python libraries / modules required:

![Environment setup](./docs/Stage%202.png)
![requirements.txt file](./docs/requiremements%20txt.png)

 - #### Stage 3:
    Start with coding the main files located in the src folder and the 5 Models located in the models folder:

![Stage 3](./docs/Stage%203.png)
![Create Models](./docs/Stage%203.1.png)

 - #### Stage 4:
    Continue to create a CLI controller and test the database relations and attributes can correctly be created, dropped and seeded with the sample information:

![Stage 4](./docs/Stage%204.png)
![Stage 4.1](./docs/cli_controller_1.png)
![Stage 4.2](./docs/cli_controller_2.png)

 - #### Stage 5:
    Start to develop the 5 contollers which are to be saved in the controllers folder:
![Stage 5](./docs/Stage%205.png)
![Stage 5.1](./docs/Stage%205.1.png)

 - #### Stage 6:
    The API testing software being used is Insomnia. In this stage setup a T2A2 folder in Insomnia and add all the http requests required for testing the 5 controller endpoints. Then start with testing just the Group & Members controllers:

![Stage 6](./docs/Stage%206.png)
![Insomnia setup](./docs/Insomnia%20HTTP%20requests%20ready%20for%20testing.png)
![Start insomnia testing](./docs/Trello%20setup%20Insomnia%20http%20requests.png)

 - #### Stage 7:
    API testing of the Bill, Outing & Invite contolllers using Insomnia:

![Stage 7](./docs/Stage%207.png)

 - #### Stage 8:
    Go back through the 5 controllers and test add the error handling options required:

![Stage 8](./docs/Stage%208.png)

 - #### Stage 9:
    Final manual testing of all controllers, models and functionality to meet project scope:

![Stage 9](./docs/Stage%209.png)

 - #### Stage 10:
    Start the documentation process:

![Stage 10](./docs/Stage%2010.png)

### 3. Third Party Services
For the development of this application the following third party services, packages or dependencies have been installed:
 - Bcrypt ver 4.2.0 & Flask-Bcrypt ver 1.0.1 (this a flask extension for bcrypt) = this is a cryptographic hash function designed for password hashing and safe storing in the backend of applications in a way that is less susceptible to dictionary-based cyberattacks. In the coding of this app it is using 2 functions:

    1 - to hash the password in the database relation when entered & saved by the user, this function is used: `bcrypt.generate_password_hash(password).decode("utf-8")`

    2 - to check the hashed password when members are logging into the app, this function is used: `bcrypt.check_password_hash(member.password, body_data.get("password")):`

 - Flask ver 3.0.3


