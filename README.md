# E-Learning Website
#### Video Demo:  <https://youtu.be/mdLrnfn5Zks>
#### Description:

Index

Index is the home page, it's an extension from layout.html.
On the home page, we have the navbar, for the images a carousel with a button that takes us to the courses page, three of the latest courses fetched from the database and the footer.
I decided to go for a white and simple UI, something clean and organized and different container colours.


Courses

The courses page it's an extension from layout.html.
On the courses page, we have the navbar, a white page presentation with two buttons, all the website available courses in the database in a greyish background and the footer.
I decided here to go with different container colours.


FAQs

The FAQs page it's an extension from layout.html.
The FAQs page would be a simple white page with FAQs. This page is still empty as I did consider this project to be a full project.


About

The about page it's an extension from layout.html.
The about page would be a simple white page it contains why this project is about.
But it lacks contact information.


------------------------------------------------------------------------------------

-- Layouts --

Layout

The layout contains the navbar, flash div and footer.
The navbar is different for non-registered users, logged-in users and admin users.
Below the navbar is the flash div.
After the main, in the end, we have a simple footer with social media links.


Layout for Sign-Up and Log-In

Mainly Bootstrap's JavaScript and CSS.


------------------------------------------------------------------------------------

Log In

The log-in page it's an extension from "layout-users.html".
It's a simple page with a logo, a flash div for any flashed messages and a form that contains: username, password and submit.
The log-in function has a JavaScript form validation and a username and password check that queries the database for validation if it succeeds then it's created a session with the user id.


Sign In

The sign-in page it's an extension from "layout-users.html".
It's a simple page with a logo, a flash div for any flashed messages and a form that contains: username, password, confirmation and submit.


------------------------------------------------------------------------------------

-- Account Button List --

Admin

Admin appears only if the user is an admin and it takes us to the admin.html page.
On the admin page, we can see all coupons. We can also choose old coupons to change, or create new coupons. After choosing our desired option we will be taken to admin_cupon.html where we change or delete old or newly created coupons.

The Admin page is supposed to have a course editor and creation option. But it's not implemented as it would require an HTML editor and it's, right now beyond my skills.


Courses

Courses takes us to the account.html.
On this page, if we haven't enrolled in any course there will be a small text with a link that redirects us to the courses page where all courses are listed.
If we have already enrolled in any course it will be here avalabe to take.


Settings

Settings takes us to the account_settings.html.
On the settings page we can change our profile picture, our password or delete our account. All of that is password protected so it's required to write our password.


------------------------------------------------------------------------------------

-- Courses --

After we click enroll in any course we will be taken to the course info (info.html) with a small box on the right with the course. The idea is that all info would be stored in the database but that is not implemented as it would be a huge project. And it would require more skills than I have.

After we click on Enroll now two things might happen:


1 Free

If it's a free course the selected course will be added to your account and you'll be redirected to your account courses.


2 Paid

If it's a paid course you will be redirected to the buy page. On the buy page, you can redeem promo codes (coupons) fill in your personal information and choose your buy method (PayPal). If everything is filled and the purchase done the course will be added to your account and you'll be redirected to your account courses.


------------------------------------------------------------------------------------