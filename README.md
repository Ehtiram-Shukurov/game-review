# Module 1 Group Assignment

CSCI 5117, Fall 2024, [assignment description](https://canvas.umn.edu/courses/460699/pages/project-1)

## App Info:

* Team Name: Big Chungus
* App Name: GameReview
* App Link: [<https://project-1-big-chungus.onrender.com/>]()

### Students

* Daniel Bielejeski, biele026@umn.edu
* Ezra Blake, shuku010@umn.edu
* Crystal Wen, wen00015@umn.edu
* William Yang, yang7313@umn.edu
* Jinming Chen, chen6386@umn.edu


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* Child Parent topic/review chain (i.e. reddit thread)
* Incorporating and extracting data from IGDB API
* Fuzzy Search

## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* ...


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**


Home page showing recently reviewed and added games. The added games would be new games that was added from IGDB API.
![home](./screenshots/home.png?raw=true)


Game page displaying the cover art, title, and summary of the game from IGDB APi. Along with sub section for users to look and post review/topics.
![game](./screenshots/game.png?raw=true)


Profile page showing an default image is the user decides to not have a profile image, and brief descriptions about the user as well as how many reviews they left on the website.
![profile](./screenshots/profile.png?raw=true)


Result page displaying the fuzzy search results where the website is searching through both its database for topics/reviews and IGDB API based on the user query
![result](./screenshots/result.png?raw=true)


Review page showing a rating and review of a game left by users, as well as the child parent post chain.
![review](./screenshots/review.png?raw=true)



## Mock-up 

There are a few tools for mock-ups. Paper prototypes (low-tech, but effective and cheap), Digital picture edition software (gimp / photoshop / etc.), or dedicated tools like moqups.com (I'm calling out moqups here in particular since it seems to strike the best balance between "easy-to-use" and "wants your money" -- the free teir isn't perfect, but it should be sufficient for our needs with a little "creative layout" to get around the page-limit)

In this space please either provide images (around 4) showing your prototypes, OR, a link to an online hosted mock-up tool like moqups.com

**[Add images/photos that show your paper prototype (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository) along with a very brief caption:**


The home page of the website, displaying general user content
![Home Page](./mockups/homePage.png?raw=true)

A login page for users to login or create an account if needed
![Login Page](./mockups/loginandsignup.png?raw=true)

A page for the individual reviews/topics created by the users, has
discussion responses as well
![Review Page](./mockups/reviewandtopic.png?raw=true)

A page for a specific game, includes different reviews and topics about the 
game
![Game Page](./mockups/gamepage.png?raw=true)

A page for the user profile
![User Profile](./mockups/userProfile.png?raw=true)

A page for the user settings
![User Settings](./mockups/settings.png?raw=true)

Link to Figma project:
https://www.figma.com/design/yl4nxmAKSPm4ww1B2vN6j5/GameReview?node-id=49-2361&t=hzYgSGKvHp1r1xso-1

## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* Library or service name: description of use
* IGDB API: used to grab relevant game data (i.e. name, genre, summary, cover art)

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

...
