# Dash_Recycle

## The Dash Button

### Configuring The Dash Button

We started the process by configuring our AWS IoT buttons via the AWS Lambda console. The configuration process requires creating/activating the certificate and private key. Once complete we then moved the certificate and authenticated private key onto the AWS IoT button. By moving the certificate and private onto the IoT button directly we are given the ability to create a AWS IoT policy which enables the button itself to make calls to the AWS IoT. The connection to AWS IoT is essential because throughout this project we utilize the AWS IoT to call a custom Lambda function that stores the users geolocation. Last but not least, associated the button to a IAM role so that the button would have the functionality to send a email upon being pressed. For more details about the AWS IoT Button Configuration  [Process please see Amazon Direction](https://docs.aws.amazon.com/iot/latest/developerguide/iot-button-quickstart.html)

### Developing The Lambda Rule

#### Desired Output Of The Lambda Rule
Great! Once the button was properly configured it was time for us to give it actual life. As mentioned in the previous section, we accomplished this goal of adding functionality to the button by using a custom Lambda function. Essentially the goal was to build a architecture that would allow the business’ customer (our indirect customer) to press the dash button and indicate the following three things with that button:
* That there was a reusable tote they would like picked up
* When they would prefer for a member of the sustainable P2P driver network to pick up the reusable tote
* Where they were located

Given that is was a large amount of information for the customer, we decided that it would be important to notify the user via email of the option(s) they had provided to us through the button.

#### Why AWS Lambda 
AWS Lambda is a Amazon service that lets users run code without needing to spend time provisioning or managing servers. This was important to use because we wanted to make sure that the product we built was only costing the business when it was in use. Additionally, we needed the system to scale automatically at a moments notice, because the business might go from having a few pickup requests a day to thousands per second. 
