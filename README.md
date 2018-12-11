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

#### How This Information Is Captured In The Lambda Rule
The AWS IoT Dash button supports three types of click: Single, Double, and Long Press. This variety of click types made it easier for us to establish a means of collecting preference type. If a user clicked the dash button of single time they were indicating that they wanted the reusable tote picked up in the Morning. A section of double clicking represented the evening and a long-press indicated flexibility. To support this we made the role wait for a click type event, and then mapped the click type to its’ respective time preference. Once completed the lambda function takes the this information and encapsulates it with the geographic coordinates stored for the button’s home address. The process of encapsulation is done by constructing a new [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) market that contains a geometry attribute holding the geographic location stored in the dash button as home, with the color property associated with the click type.

Next in the process is merging this new geometry attribute with the collection of existing geometry attributes which are stored in a large GeoJSON file. (Each geometry attribute represents a indirect customer that the business (our direct customer) must server either by picking up a reusable tote or delivering a item in a reusable tote to.) To merge we check our existing GeoJSON file to see if the geometry attribute already exists, if it does we delete it from the record and update it with the newly constructed geometry attribute. This is information because it allows our indirect customer to change their mind about their preference as much as they want and still have it update real time without creating duplicate pins that the business would see on their end. Upon the successful merging, the function then automatically updates the existing GeoJSON file that is hosted in a AWS S3 bucket with the newly merged file. In an effort, to provide clarity behind what the GeoJSON file looks like we have provide a [script that creates a dummy GeoJSON file](https://github.com/CMine/Dash_Recycle/blob/master/GeoJson/generateGeoJSON.py) styled like the actual file we have hosted in the S3 bucket and the [resulting GeoJSON file](https://github.com/CMine/Dash_Recycle/blob/master/GeoJson/pickups.geojson) returned from the script.  


#### Why AWS Lambda 
AWS Lambda is a Amazon service that lets users run code without needing to spend time provisioning or managing servers. This was important to use because we wanted to make sure that the product we built was only costing the business when it was in use. Additionally, we needed the system to scale automatically at a moments notice, because the business might go from having a few pickup requests a day to thousands per second. 

## Mathematical Model
A mathematical model had to be build to model the Vehicle Routing Problem using the Clarke and Wright Savings Algorithm as described [here](http://web.mit.edu/urban_or_book/www/book/chapter6/6.4.12.html). The Vehicle Routing Problem in our problem is modelled such that it takes into account of constraints such as the customer preference for pick-up, the customer locality, maximum load of each vehicle and the number  of vehicles available for routing. The final file containing the key functions used are in the ipynotebook titled [Final Vehicle Routing Problem](https://github.com/CMine/Dash_Recycle/blob/master/Math_Model/Final_Vehicle%20Routing%20Problem.ipynb). Below are some key functions that the python script uses to solve the routing problem

### Getting the Points from AWS
Pulling from the S3 bucket, we are able to obtain the geolocation data and customer preference that is stored when a Dash Button is pressed.

### Getting the Distances
Routing over a route network is different from routing over an unconstrained 2 dimensional space. As such, we utilize the [Open Source Routing Machine](http://router.project-osrm.org) to request for a duration matrix for all the points of interest. This returns the shortest times, and in turn distance, between each of the location retrieved from the S3 bucket.

### Clarke Wright Algorithm
With the distance matrix the Clarke Wright Algorithm is able to calculate the Savings Matrix, where each entry s(i,j) represent the savings of joining point i to point j versus the sum of going from the origin to point i and back and origin to point j and back as described by the following equation.  
<img src="https://latex.codecogs.com/gif.latex?$$s(i,j)&space;=&space;d(o,i)&space;&plus;&space;d(o,j)&space;-&space;d(i,j)$$" title="$$s(i,j) = d(o,i) + d(o,j) - d(i,j)$$" />
The larger the savings, the more inclined this algorithm is likely to want to place these points together to reduce the distance travelled. As such the algorithm goes down the savings in descending order and appends this i-j link on the routes if the following conditions are met:  
1. Constraints are not violated, i.e. maximum load, customer preferences are not violated  
2. Neither i or j are already in routes, in which case a new route is created  
3. Either i or j are in routes but not in the interior of the routes, in which case the other point is included into the route  
4. Both i and j are in seperate routes but not in the interior of the routes, in which both routes are joined at i-j  
The algorithm continues until the algorithm has run through all points in the savings list (with positive savings).

### Routing Details
Next, routing details, such as directions and total distances travelled for the routes are extracted from [Open Source Routing Machine](http://router.project-osrm.org). This provides information on the increase in distance required to undertake the additional pick-ups of re-useable totes.

### Environmental Details
Finally, the distances, cardboard and reuseable totes are converted to carbon dioxide emissions to assess the environmental impact of the Green Route blueprint. The total carbon emission of the routes and the re-useable totes are compared to the status quo of just covering shorter distances but incurring repeated carbon costs from manufacturing cardboard boxes to obtain the yearly carbon savings and its equivalent number of trees, in terms of trees required to sequester the carbon saved. 
