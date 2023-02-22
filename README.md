
# ***Disclaimer***
### This project is based on the TV Maze API, which provides a detailed list of TV shows and people. It is just a course exercise.
<br>

# Environment
Python 3.9.12  
Flask 2.0.0  
Werkzeug 2.0.0  
flask-restx 0.5.1  
sqlite3 3.38.2  
pandas 1.4.2
<br>

# How to use this APIs
1, Open the cmd and type in "python RESTful_api_for_actors.py".  
2, Open the link http://127.0.0.1:5729/ in your browser.  
3, Use **POST** method to add the actors into the database. (The initial state of database is empty, you have to add some actors/actresses into it).  

# Functions
### 1, POST method: url: /actors  
enter a name, if the name is in TV Maze's database, the api will store the information into our local databse.   
**example:** entering 'Elizabeth Olsen'
![post example](.\img\post.png "create an actor")
<br><br>

### 2, GET method: url: /actor/{id}
This operation retrieves an actor by their lD.
**example:** entering '4'
![get by ID example](img\getID.png "get an actor's infomation by id")
<br><br>

### 3, DELETE method: url: /actor/{id}
This operation deletes an existing actor from the database.  
**example:** entering '6'
![delete example](img\delete0.png "delete an actor's infomation by id")  
**before deleting:**
![before deleting](img\delete1.png "before deleting")    
**after deleting:**
![after deleting](img\delete2.png "after deleting")  
<br><br>

### 4,  PATCH method: url: /actor/{id}  
This operation partially updates the details of an actor. (The identifier cannot be changed)
**example:** 
![patch example](img\patch.png "patch")   
**before update:**
![before patcb](img\delete2.png "before patch")    
**after update:**
![get by ID example](img\patch1.png "after patch")    
<br><br>

### 5,  GET method: url: /actor
This operation retrieves all available actors. All four parameters are optional with default values being "order=+id", "page=1", and "size =10",filter="id,name". "page" and "size" are used for pagination; "size" shows the number of actors per page. "order" is a comma-separated string value to sort the list based on the given criteria, The string consists of two parts.the first part is a special character '+' or '-' where '+' indicates ordering ascendingly, and '-' indicates orderingdescendingly. The second part is an attribute name which is one of {id, name, country, birthday, deathday, last-update}.  
**example:** 
![get  example](img\getAll0.png "get") 
![get  example](img\getAll1.png "get")   
<br><br>

### 6, GET method: url: /actor/statistics
This operation accepts a parameter called "format" which can be either "json" or "image". 
Actors break down by an attribute determined by the "by" parameter (a comma-separated value); this parameter can be any of the following Actors' attributes: "country" (showing the percentage of actors per country), "birthday", "gender", and "life status" (represents what percentages of actors are alive).   
**example:**   
**get json:** 
![get  json example](img\getJson.png "get json")   
**get image:** 
![get  json example](img\getImage.png "get image") 




