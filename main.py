from SETTINGS import *


@app.route("/")
def home():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
        print(current_user.access_token)
    return render_template("home.html", current_user=current_user)


@app.route("/oauth/callback")
def callback():
    current_user = User(request.args["code"])
    session["token"] = current_user.access_token
    d = dataManager()
    if d.get("users", current_user.user["id"]):
        # Update
        d.update(
            "users", ["data"], [str(current_user.__dict__)], current_user.user["id"]
        )  # Update User
        print("Update User.")
    else:
        d.is_registered(
            "users",
            current_user.user["id"],
            True,
            (
                DB_USERS_TABLE_COLUMNS,
                [current_user.user["id"], str(current_user.__dict__)],
            ),
        )
    return redirect("/")


@app.route("/logout")
def logout():
    if "token" in session:
        session.clear()
        return redirect("/")


@app.route("/u")
def user():
    userId = request.args["id"]
    d = dataManager()

    u = User(id=userId)
    u.getMeInDatabase()
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))

    return render_template("user.html", current_user=current_user, user=u)


@app.route("/config", methods=["POST", "get"])
def config():
    current_user = None
    if "token" in session:
        current_user = User()
        current_user.loadAccessToken(session.get("token"))
    if current_user and request.method == "POST":
        color = request.form.get("highlight")  # Highlight color
        about = request.form.get("about")  # About
        urls = request.form.get('url_index') # get urls
        urlsDict = {}
        if int(urls) > 1:
            for url in range(int(urls)):
                x = {}
                x['title'] = request.form.get('url-title'+str(url))
                x['url'] = request.form.get('url-url'+str(url))
                urlsDict[str(url)] = x

        if (about in ["",' ', None, "None"]) or len(about) < 3:
            about = "Olá!"

        d = dataManager()
        # Update user
        current_user.highlight_color = color
        current_user.aboutme = about
        current_user.links = urlsDict
        
        d.update('users',DB_USERS_TABLE_COLUMNS[1:],(str(current_user.__dict__),),current_user.id) # update in database
    return render_template("config.html", current_user=current_user)


# Files Returners
@app.route("/about.html")
def about():
    f = open(app.template_folder + "/about.html", "rb").read()
    return f


if __name__ == "__main__":
    app.run(debug=True)
