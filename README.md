# Green Route

This project was original entitled *Dash Recycle*, but has since be renamed to **Green Route**. To maintain data stewardship we have opted not to rename the repository and instead provide this notification.

## Product Narrative

Green Route is a new on-demand P2P delivery model that empowers small/medium sized business to deploy a small sustainable network of flexible couriers to deliver packages in reusable totes and later pick up those totes at the customers convenience. All with the press of a button.

## The Dash Button

### Configuring The Dash Button

We started the process by configuring our AWS IoT buttons via the AWS Lambda console. The configuration process requires creating/activating the certificate and private key. Once complete we then moved the certificate and authenticated private key onto the AWS IoT button. By moving the certificate and private onto the IoT button directly we are given the ability to create a AWS IoT policy which enables the button itself to make calls to the AWS IoT. The connection to AWS IoT is essential because throughout this project we utilize the AWS IoT to call a custom Lambda function that stores the users geolocation. Last but not least, associated the button to a IAM role so that the button would have the functionality to send a email upon being pressed. For more details about the AWS IoT Button Configuration process please see [Amazon Documentation Directly](https://docs.aws.amazon.com/iot/latest/developerguide/iot-button-quickstart.html)

### Developing The Lambda Rule

#### Desired Output Of The Lambda Rule
Great! Once the button was properly configured it was time for us to give it actual life. As mentioned in the previous section, we accomplished this goal of adding functionality to the button by using a custom Lambda function. Essentially the goal was to build a architecture that would allow the business’ customer (our indirect customer) to press the dash button and indicate the following three things with that button:
* That there was a reusable tote they would like picked up
* When they would prefer for a member of the sustainable P2P driver network to pick up the reusable tote
* Where they were located

Given that is was a large amount of information for the customer, we decided that it would be important to notify the user via email of the option(s) they had provided to us through the button.

### How This Information Is Captured In The Lambda Rule
The AWS IoT Dash button supports three types of click: Single, Double, and Long Press. This variety of click types made it easier for us to establish a means of collecting preference type. If a user clicked the dash button of single time they were indicating that they wanted the reusable tote picked up in the Morning. A section of double clicking represented the evening and a long-press indicated flexibility. To support this we made the role wait for a click type event, and then mapped the click type to its’ respective time preference. Once completed the lambda function takes the this information and encapsulates it with the geographic coordinates stored for the button’s home address. The process of encapsulation is done by constructing a new [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) market that contains a geometry attribute holding the geographic location stored in the dash button as home, with the color property associated with the click type.

Next in the process is merging this new geometry attribute with the collection of existing geometry attributes which are stored in a large GeoJSON file. (Each geometry attribute represents a indirect customer that the business (our direct customer) must server either by picking up a reusable tote or delivering a item in a reusable tote to.) To merge we check our existing GeoJSON file to see if the geometry attribute already exists, if it does we delete it from the record and update it with the newly constructed geometry attribute. This is information because it allows our indirect customer to change their mind about their preference as much as they want and still have it update real time without creating duplicate pins that the business would see on their end. Upon the successful merging, the function then automatically updates the existing GeoJSON file that is hosted in a AWS S3 bucket with the newly merged file. In an effort, to provide clarity behind what the GeoJSON file looks like we have provide a [script that creates a dummy GeoJSON file](https://github.com/CMine/Dash_Recycle/blob/master/GeoJson/generateGeoJSON.py) styled like the actual file we have hosted in the S3 bucket and the [resulting GeoJSON file](https://github.com/CMine/Dash_Recycle/blob/master/GeoJson/pickups.geojson) returned from the script.  


#### Why AWS Lambda 
AWS Lambda is a Amazon service that lets users run code without needing to spend time provisioning or managing servers. This was important to use because we wanted to make sure that the product we built was only costing the business when it was in use. Additionally, we needed the system to scale automatically at a moments notice, because the business might go from having a few pickup requests a day to thousands per second. 
